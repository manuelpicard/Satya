"""
celo_readonly.py - strictly read-only access layer for Celo Mainnet.

Safety design
- Only the JSON-RPC methods in ALLOWED_RPC_METHODS can be sent. Everything else
  (eth_sendTransaction, eth_sendRawTransaction, eth_sign, personal_sign,
  eth_signTypedData*, wallet_*, ...) raises before any network access.
- eth_call is sent without a "from" field and is executed by the node as a
  simulation; it cannot change state or create a transaction.
- Blockscout is accessed only via HTTP GET.
- No keys, seeds, passwords or signing libraries are used or accepted.
"""
from __future__ import annotations

import json
import re
import time
from decimal import Decimal, getcontext

import requests
from Crypto.Hash import keccak

getcontext().prec = 80

RPC_URL = "https://forno.celo.org"
BLOCKSCOUT_API = "https://celo.blockscout.com/api/v2"
EXPLORER = "https://celo.blockscout.com"
EXPECTED_CHAIN_ID = 42220

ALLOWED_RPC_METHODS = frozenset({
    "eth_chainId",
    "eth_blockNumber",
    "eth_getBalance",
    "eth_call",
    "eth_getBlockByNumber",
    "eth_getCode",
})

# Configured, user-specified contracts (Celo Mainnet)
TOKENS = {
    "USDT": {"address": "0x48065fbBE25f71C9282ddf5e1cD6D6A887483D5e", "decimals": 6,
              "expected_symbols": ["USD₮", "USDT"]},
    "USDC": {"address": "0xcebA9300f2b948710d2653dD7B07f33A8B32118C", "decimals": 6,
              "expected_symbols": ["USDC"]},
    "USDm": {"address": "0x765DE816845861e75A25fCA122bb6898B8B1282a", "decimals": 18,
              "expected_symbols": ["USDm", "cUSD"]},
    "EURm": {"address": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73", "decimals": 18,
              "expected_symbols": ["EURm", "cEUR"]},
}
VAULTS = {
    "mpAaveUSDT": {"address": "0xbaD4711D689329E315Be3E7C1C64CF652868C56c",
                    "label": "MiniPay Aave V3 USDT"},
    "mpFeatherUSDT": {"address": "0x440933053Fb430cABf8152F59F5967cE0FeB5f15",
                       "label": "MiniPay Morpho Feather USDT"},
}

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

_session = requests.Session()
_session.headers.update({"User-Agent": "minipay-readonly-monitor/1.0"})

# Audit trail: every network access is counted here and reported.
AUDIT = {"rpc": {}, "http_get": {}}


def _audit(kind: str, key: str) -> None:
    AUDIT[kind][key] = AUDIT[kind].get(key, 0) + 1


_last_http = [0.0]
MIN_HTTP_INTERVAL = 0.35  # seconds between Blockscout requests (polite throttling)


def _throttle() -> None:
    wait = MIN_HTTP_INTERVAL - (time.time() - _last_http[0])
    if wait > 0:
        time.sleep(wait)
    _last_http[0] = time.time()


# --------------------------------------------------------------------------- #
# Hashing / address helpers
# --------------------------------------------------------------------------- #
def keccak_hex(data: bytes) -> str:
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.hexdigest()


def selector(signature: str) -> str:
    return "0x" + keccak_hex(signature.encode())[:8]


def topic(signature: str) -> str:
    return "0x" + keccak_hex(signature.encode())


def to_checksum(addr: str) -> str:
    a = addr.lower().replace("0x", "")
    h = keccak_hex(a.encode())
    return "0x" + "".join(c.upper() if int(h[i], 16) >= 8 else c for i, c in enumerate(a))


ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def validate_address(raw: str) -> dict:
    """Pure offline syntax check (no network access)."""
    s = raw.strip()
    result = {"input": raw, "trimmed": s, "valid": False, "checks": []}
    if len(s) != 42:
        result["checks"].append(f"Länge {len(s)} statt 42 Zeichen")
        return result
    if not s.startswith("0x"):
        result["checks"].append("Präfix '0x' fehlt")
        return result
    if not ADDR_RE.match(s):
        result["checks"].append("enthält Zeichen außerhalb 0-9/a-f/A-F")
        return result
    body = s[2:]
    checksum = to_checksum(s)
    if body.islower() or body.isupper():
        result["checks"].append("einheitliche Groß-/Kleinschreibung: keine EIP-55-Prüfsumme enthalten (zulässig)")
        result["eip55"] = "nicht vorhanden"
    elif s == checksum:
        result["checks"].append("EIP-55-Prüfsumme korrekt")
        result["eip55"] = "korrekt"
    else:
        result["checks"].append("EIP-55-Prüfsumme FALSCH - möglicher Tippfehler")
        result["eip55"] = "falsch"
        return result
    if s.lower() == ZERO_ADDRESS:
        result["checks"].append("Null-Adresse ist keine Wallet")
        return result
    result["valid"] = True
    result["checksum"] = checksum
    result["short"] = f"{checksum[:6]}…{checksum[-4:]}"
    return result


# --------------------------------------------------------------------------- #
# JSON-RPC (read-only whitelist)
# --------------------------------------------------------------------------- #
class ReadOnlyViolation(RuntimeError):
    pass


_rpc_id = 0


def rpc(method: str, params: list, retries: int = 3):
    global _rpc_id
    if method not in ALLOWED_RPC_METHODS:
        raise ReadOnlyViolation(f"RPC-Methode '{method}' ist nicht erlaubt (Nur-Lese-Modus)")
    if method == "eth_call":
        call = params[0]
        if any(k in call for k in ("from", "value", "gas", "gasPrice")):
            raise ReadOnlyViolation("eth_call darf nur 'to' und 'data' enthalten")
    _rpc_id += 1
    payload = {"jsonrpc": "2.0", "id": _rpc_id, "method": method, "params": params}
    _audit("rpc", method)
    last = None
    for attempt in range(retries):
        try:
            r = _session.post(RPC_URL, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(f"RPC-Fehler {method}: {data['error']}")
            return data["result"]
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"RPC {method} fehlgeschlagen: {last}")


def chain_id() -> int:
    return int(rpc("eth_chainId", []), 16)


def block_number() -> int:
    return int(rpc("eth_blockNumber", []), 16)


def get_block(number: int) -> dict:
    return rpc("eth_getBlockByNumber", [hex(number), False])


def get_balance(addr: str, block: int) -> int:
    return int(rpc("eth_getBalance", [addr, hex(block)]), 16)


def get_code(addr: str, block: int) -> str:
    return rpc("eth_getCode", [addr, hex(block)])


def _enc_addr(a: str) -> str:
    return a.lower().replace("0x", "").rjust(64, "0")


def _enc_uint(v: int) -> str:
    return hex(v)[2:].rjust(64, "0")


def eth_call(to: str, data: str, block: int) -> str:
    return rpc("eth_call", [{"to": to, "data": data}, hex(block)])


def call_uint(to: str, sig: str, block: int, *args) -> int:
    data = selector(sig) + "".join(args)
    res = eth_call(to, data, block)
    return int(res, 16) if res and res != "0x" else 0


def call_address(to: str, sig: str, block: int) -> str:
    res = eth_call(to, selector(sig), block)
    return to_checksum("0x" + res[-40:])


def _decode_string(res: str) -> str:
    raw = bytes.fromhex(res[2:])
    if len(raw) == 32:  # bytes32 style
        return raw.rstrip(b"\x00").decode("utf-8", "replace")
    off = int.from_bytes(raw[0:32], "big")
    ln = int.from_bytes(raw[off:off + 32], "big")
    return raw[off + 32: off + 32 + ln].decode("utf-8", "replace")


def call_string(to: str, sig: str, block: int) -> str:
    return _decode_string(eth_call(to, selector(sig), block))


def fmt_units(raw: int, decimals: int) -> Decimal:
    return Decimal(raw) / (Decimal(10) ** decimals)


# --------------------------------------------------------------------------- #
# Blockscout (HTTP GET only)
# --------------------------------------------------------------------------- #
def bs_get(path: str, params: dict | None = None, retries: int = 6) -> dict:
    url = f"{BLOCKSCOUT_API}{path}"
    _audit("http_get", "blockscout_api_v2")
    last = None
    for attempt in range(retries):
        try:
            _throttle()
            r = _session.get(url, params=params, timeout=40)
            if r.status_code == 429:
                last = "HTTP 429 (Rate-Limit)"
                time.sleep(min(60, 4 * 2 ** attempt))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(30, 2 * 2 ** attempt))
    raise RuntimeError(f"Blockscout GET {path} fehlgeschlagen: {last}")


BLOCKSCOUT_V1 = "https://celo.blockscout.com/api"


def bs_v1_get(params: dict, retries: int = 7) -> dict:
    """Etherscan-compatible Blockscout endpoint (GET only), used for topic-filtered logs."""
    _audit("http_get", "blockscout_api_v1_getLogs")
    last = None
    for attempt in range(retries):
        try:
            _throttle()
            r = _session.get(BLOCKSCOUT_V1, params=params, timeout=60)
            if r.status_code == 429:
                last = "HTTP 429 (Rate-Limit)"
                time.sleep(min(60, 4 * 2 ** attempt))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(30, 2 * 2 ** attempt))
    raise RuntimeError(f"Blockscout v1 GET fehlgeschlagen: {last}")


def get_logs_all(address: str, topics: dict, from_block: int = 0, to_block: int | None = None,
                 max_rounds: int = 200):
    """Topic-filtered event logs with block-based pagination (1000 per request).
    topics: e.g. {"topic0": "0x..", "topic2": "0x.."}; AND-combined."""
    keys = sorted(topics)
    params = {"module": "logs", "action": "getLogs", "address": address,
              "toBlock": str(to_block) if to_block is not None else "latest", **topics}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            params[f"{a}_{b[-1]}_opr"] = "and"
    seen, out, complete = set(), [], True
    fb = from_block
    for _ in range(max_rounds):
        params["fromBlock"] = str(fb)
        j = bs_v1_get(params)
        res = j.get("result") or []
        if j.get("status") == "0" and "No logs" not in (j.get("message") or ""):
            raise RuntimeError(f"getLogs Fehler: {j.get('message')} {str(j.get('result'))[:200]}")
        new = 0
        for lg in res:
            k = (lg["transactionHash"], int(lg["logIndex"], 16) if str(lg["logIndex"]).startswith("0x") else int(lg["logIndex"] or 0))
            if k in seen:
                continue
            seen.add(k)
            out.append(lg)
            new += 1
        if len(res) < 1000:
            break
        last_block = int(res[-1]["blockNumber"], 16)
        if new == 0:
            fb = last_block + 1
        else:
            fb = last_block
        time.sleep(0.3)
    else:
        complete = False
    return out, complete


def topic_addr(a: str) -> str:
    return "0x" + a.lower().replace("0x", "").rjust(64, "0")


def bs_paginate(path: str, params: dict | None = None, stop_before_ts: float | None = None,
                max_pages: int = 200, ts_field: str = "timestamp"):
    """Yield items over all pages; stop when items become older than stop_before_ts."""
    params = dict(params or {})
    pages = 0
    complete = True
    while True:
        data = bs_get(path, params)
        items = data.get("items", [])
        stop = False
        for it in items:
            ts = it.get(ts_field)
            if stop_before_ts is not None and ts:
                from datetime import datetime
                t = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                if t < stop_before_ts:
                    stop = True
                    break
            yield it
        pages += 1
        nxt = data.get("next_page_params")
        if stop or not nxt:
            break
        if pages >= max_pages:
            complete = False
            break
        params = {**{k: v for k, v in params.items() if k in ("type", "filter", "token")}, **nxt}
        time.sleep(0.25)
    bs_paginate.last_complete = complete  # type: ignore[attr-defined]
    bs_paginate.last_pages = pages  # type: ignore[attr-defined]


def tx_link(h: str) -> str:
    return f"{EXPLORER}/tx/{h}"


def addr_link(a: str) -> str:
    return f"{EXPLORER}/address/{a}"


if __name__ == "__main__":
    print(json.dumps({"chain_id": chain_id(), "block": block_number()}))
