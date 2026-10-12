"""
minipay_report.py - read-only MiniPay wallet report for Celo Mainnet (chain id 42220).

Usage
  python3 minipay_report.py validate <0x-address>
  python3 minipay_report.py report   <0x-address> --confirmed [--days N] [--out DIR]
  python3 minipay_report.py bind     <0x-address> --consent --account-label <email>

Guarantees
- Uses only read methods (see celo_readonly.ALLOWED_RPC_METHODS) and HTTP GET.
- Never asks for, accepts or stores passwords, private keys, seed/recovery phrases,
  SMS or 2FA codes. There is no code path that signs or sends a transaction.
- "report" refuses to run without --confirmed (user confirmed the shown address).
- The address-to-account binding is only written by "bind" with --consent.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

import celo_readonly as c

UTC = timezone.utc
T_DEPOSIT = c.topic("Deposit(address,address,uint256,uint256)")
T_WITHDRAW = c.topic("Withdraw(address,address,address,uint256,uint256)")
T_TRANSFER = c.topic("Transfer(address,address,uint256)")

VERIFIED_TOKEN_ADDRS = {t["address"].lower(): k for k, t in c.TOKENS.items()}
VAULT_ADDRS = {v["address"].lower(): k for k, v in c.VAULTS.items()}
USDT_ADDR = c.TOKENS["USDT"]["address"].lower()

# Boost heuristic parameters (documented in the report)
BOOST_MIN_TRANSFERS = 3
BOOST_MIN_DISTINCT_DAYS = 3
BOOST_DAILY_TOLERANCE_H = 4
BOOST_MIN_REGULAR_SHARE = 0.6
BOOST_MAX_SINGLE_USDT = Decimal("10")
BOOST_DISTRIBUTOR_MIN_TRANSFERS = 10_000
MAX_SENDER_PROFILES = 300

CAT_BOOST = "Möglicher MiniPay-Boost-Ertrag – nicht abschließend zuordenbar"
CAT_P2P = "P2P-Eingang (wahrscheinlich)"
CAT_RAMP = "On-Ramp / Bridge / Dienstleister (möglich)"
CAT_REFUND = "Rückzahlung / Erstattung (möglich)"
CAT_UNKNOWN = "Unbekannter Eingang"
CAT_VAULT_OUT = "Vault-Auszahlung (MiniPay Earn)"
CAT_VAULT_IN = "Vault-Einzahlung (MiniPay Earn)"
CAT_VAULT_SHARE = "Vault-Anteile (Mint/Burn/Transfer)"
CAT_OUTGOING = "Ausgang (sonstige Bewegung)"
CAT_UNVERIFIED = "Unverifizierter Token – nicht in Summen"


def utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def parse_ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def short(a: str) -> str:
    return f"{a[:6]}…{a[-4:]}" if a else "–"


def dfmt(d: Decimal, places: int = 6) -> str:
    q = Decimal(1).scaleb(-places)
    d = Decimal(str(d))
    return f"{d.quantize(q):,}".replace(",", "\u202f")


# --------------------------------------------------------------------------- #
# Step: balances
# --------------------------------------------------------------------------- #
def read_balances(addr: str, blk: int) -> dict:
    res = {"native": {}, "tokens": {}, "errors": []}
    raw = c.get_balance(addr, blk)
    res["native"] = {"asset": "CELO (nativ)", "raw": str(raw), "decimals": 18,
                     "formatted": str(c.fmt_units(raw, 18)), "method": "eth_getBalance",
                     "block": blk}
    for key, t in c.TOKENS.items():
        a = t["address"]
        rec = {"key": key, "contract": a}
        try:
            sym = c.call_string(a, "symbol()", blk)
            dec = c.call_uint(a, "decimals()", blk)
            bal = c.call_uint(a, "balanceOf(address)", blk, c._enc_addr(addr))
            rec.update({"symbol_onchain": sym, "decimals_onchain": dec,
                        "decimals_expected": t["decimals"],
                        "metadata_verified": (dec == t["decimals"] and sym in t["expected_symbols"]),
                        "raw": str(bal), "formatted": str(c.fmt_units(bal, dec)),
                        "method": "eth_call balanceOf/symbol/decimals", "block": blk})
        except Exception as e:  # noqa: BLE001
            rec["error"] = str(e)[:300]
            res["errors"].append(f"{key}: {e}")
        res["tokens"][key] = rec
    return res


def read_other_tokens(addr: str) -> tuple[list, list]:
    """All token balances known to Blockscout; anything not configured is 'unverifiziert'."""
    errors = []
    try:
        items = c.bs_get(f"/addresses/{addr}/token-balances")
    except Exception as e:  # noqa: BLE001
        return [], [f"Blockscout token-balances: {e}"]
    out = []
    for it in items if isinstance(items, list) else []:
        tok = it.get("token") or {}
        ta = (tok.get("address_hash") or tok.get("address") or "").lower()
        if ta in VERIFIED_TOKEN_ADDRS or ta in VAULT_ADDRS:
            continue
        dec = tok.get("decimals")
        try:
            fmt = str(c.fmt_units(int(it.get("value") or 0), int(dec))) if dec not in (None, "") else it.get("value")
        except Exception:  # noqa: BLE001
            fmt = it.get("value")
        lookalike = any(s.lower() in (tok.get("symbol") or "").lower() for s in
                        ["usdt", "usd₮", "usdc", "cusd", "usdm", "eurm", "ceur", "celo", "minipay", "mpaave", "mpfeather"])
        out.append({"contract": c.to_checksum(ta) if ta else None, "name": tok.get("name"),
                    "symbol": tok.get("symbol"), "type": tok.get("type"), "decimals": dec,
                    "raw": it.get("value"), "formatted": fmt, "token_id": it.get("token_id"),
                    "blockscout_is_scam": (tok.get("reputation") == "scam"),
                    "lookalike_symbol": lookalike, "status": "unverifiziert – nicht in Summen"})
    return out, errors


# --------------------------------------------------------------------------- #
# Step: transfer history
# --------------------------------------------------------------------------- #
def fetch_token_transfers(addr: str, since_ts: float | None) -> tuple[list, dict]:
    items = list(c.bs_paginate(f"/addresses/{addr}/token-transfers", {}, stop_before_ts=since_ts,
                               max_pages=400))
    meta = {"pages": c.bs_paginate.last_pages, "complete": c.bs_paginate.last_complete,
            "count": len(items)}
    return items, meta


def fetch_native_incoming(addr: str, since_ts: float | None) -> tuple[list, dict]:
    out, metas = [], {}
    txs = list(c.bs_paginate(f"/addresses/{addr}/transactions", {"filter": "to"},
                             stop_before_ts=since_ts, max_pages=200))
    metas["transactions"] = {"pages": c.bs_paginate.last_pages, "complete": c.bs_paginate.last_complete}
    for t in txs:
        if int(t.get("value") or 0) > 0 and (t.get("to") or {}).get("hash", "").lower() == addr.lower() \
                and t.get("status") in (None, "ok"):
            out.append({"timestamp": t["timestamp"], "block": t.get("block_number"), "tx": t["hash"],
                        "from": (t.get("from") or {}).get("hash"), "raw": t["value"], "kind": "Transaktion"})
    itxs = list(c.bs_paginate(f"/addresses/{addr}/internal-transactions", {"filter": "to"},
                              stop_before_ts=since_ts, max_pages=200))
    metas["internal"] = {"pages": c.bs_paginate.last_pages, "complete": c.bs_paginate.last_complete}
    for t in itxs:
        if int(t.get("value") or 0) > 0 and (t.get("to") or {}).get("hash", "").lower() == addr.lower() \
                and t.get("success", True):
            out.append({"timestamp": t["timestamp"], "block": t.get("block_number"),
                        "tx": t["transaction_hash"], "from": (t.get("from") or {}).get("hash"),
                        "raw": t["value"], "kind": "interne Transaktion"})
    return out, metas


# --------------------------------------------------------------------------- #
# Step: vault events
# --------------------------------------------------------------------------- #
def _u256(data: str, idx: int) -> int:
    d = data[2:]
    return int(d[idx * 64:(idx + 1) * 64], 16)


def _addr_from_topic(t: str) -> str:
    return c.to_checksum("0x" + t[-40:])


def _hexint(v) -> int:
    if isinstance(v, int):
        return v
    v = str(v)
    return int(v, 16) if v.startswith("0x") else int(v or 0)


def _decode_vault_log(bucket: str, tp: list, data: str, base: dict) -> dict | None:
    if bucket == "deposits":
        base.update({"sender": _addr_from_topic(tp[1]), "owner": _addr_from_topic(tp[2]),
                     "assets_raw": _u256(data, 0), "shares_raw": _u256(data, 1)})
    elif bucket == "withdrawals":
        base.update({"sender": _addr_from_topic(tp[1]), "receiver": _addr_from_topic(tp[2]),
                     "owner": _addr_from_topic(tp[3]),
                     "assets_raw": _u256(data, 0), "shares_raw": _u256(data, 1)})
    else:
        frm, to = _addr_from_topic(tp[1]), _addr_from_topic(tp[2])
        if frm.lower() == c.ZERO_ADDRESS or to.lower() == c.ZERO_ADDRESS:
            return None  # mint/burn already represented by Deposit/Withdraw
        base.update({"from": frm, "to": to, "shares_raw": _u256(data, 0)})
    return base


def vault_events_from_tx_logs(addr: str, vault: str, tx_hashes: list[str]) -> dict:
    """Fallback (Blockscout v2 only): decode vault events from the logs of the
    transactions in which this wallet moved vault shares. Limited to the fetched window."""
    al, vl = addr.lower()[2:], vault.lower()
    res = {"deposits": [], "withdrawals": [], "share_in": [], "share_out": [], "complete": True,
           "errors": [], "source": "Fallback: /transactions/{hash}/logs (nur abgefragter Zeitraum)"}
    for h in sorted(set(tx_hashes)):
        try:
            d = c.bs_get(f"/transactions/{h}/logs")
        except Exception as e:  # noqa: BLE001
            res["errors"].append(f"{h[:10]}…: {e}")
            res["complete"] = False
            continue
        for lg in d.get("items", []):
            if (lg.get("address") or {}).get("hash", "").lower() != vl:
                continue
            tp = lg.get("topics") or []
            tp = [t for t in tp if t]
            if not tp:
                continue
            ts = parse_ts(lg["block_timestamp"]) if lg.get("block_timestamp") else 0
            base = {"tx": h, "block": int(lg.get("block_number") or 0), "timestamp": int(ts),
                    "log_index": int(lg.get("index") or 0)}
            if tp[0] == T_DEPOSIT and len(tp) >= 3 and al in (tp[1][-40:].lower(), tp[2][-40:].lower()):
                r = _decode_vault_log("deposits", tp, lg["data"], base)
                res["deposits"].append(r)
            elif tp[0] == T_WITHDRAW and len(tp) >= 4 and al in (tp[2][-40:].lower(), tp[3][-40:].lower()):
                r = _decode_vault_log("withdrawals", tp, lg["data"], base)
                res["withdrawals"].append(r)
            elif tp[0] == T_TRANSFER and len(tp) >= 3:
                if tp[2][-40:].lower() == al:
                    r = _decode_vault_log("share_in", tp, lg["data"], base)
                    if r:
                        res["share_in"].append(r)
                elif tp[1][-40:].lower() == al:
                    r = _decode_vault_log("share_out", tp, lg["data"], base)
                    if r:
                        res["share_out"].append(r)
    for b in ("deposits", "withdrawals", "share_in", "share_out"):
        res[b].sort(key=lambda x: (x["block"], x["log_index"]))
    return res


def fetch_vault_events(addr: str, vault: str, share_tx_hashes: list[str] | None = None) -> dict:
    ta = c.topic_addr(addr)
    res = {"deposits": [], "withdrawals": [], "share_in": [], "share_out": [], "complete": True, "errors": [],
           "source": "Blockscout getLogs (gesamter Verlauf, nach Topics gefiltert)"}
    queries = [
        ("deposits", {"topic0": T_DEPOSIT, "topic2": ta}),   # owner = user
        ("deposits", {"topic0": T_DEPOSIT, "topic1": ta}),   # sender = user
        ("withdrawals", {"topic0": T_WITHDRAW, "topic3": ta}),  # owner = user
        ("withdrawals", {"topic0": T_WITHDRAW, "topic2": ta}),  # receiver = user
        ("share_in", {"topic0": T_TRANSFER, "topic2": ta}),
        ("share_out", {"topic0": T_TRANSFER, "topic1": ta}),
    ]
    seen = set()
    for bucket, topics in queries:
        try:
            logs, complete = c.get_logs_all(vault, topics)
        except Exception as e:  # noqa: BLE001
            # Primary source failed -> fall back to per-transaction logs
            fb = vault_events_from_tx_logs(addr, vault, share_tx_hashes or [])
            fb["errors"].insert(0, f"Primärquelle getLogs fehlgeschlagen ({bucket}: {e}); Ausweichroute verwendet")
            fb["complete"] = False  # window-limited by construction
            return fb
        res["complete"] &= complete
        for lg in logs:
            key = (bucket, lg["transactionHash"], _hexint(lg["logIndex"]))
            if key in seen:
                continue
            seen.add(key)
            tp = lg["topics"]
            tp = [t for t in tp if t]
            base = {"tx": lg["transactionHash"], "block": _hexint(lg["blockNumber"]),
                    "timestamp": _hexint(lg["timeStamp"]), "log_index": _hexint(lg["logIndex"])}
            r = _decode_vault_log(bucket, tp, lg["data"], base)
            if r:
                res[bucket].append(r)
    for b in ("deposits", "withdrawals", "share_in", "share_out"):
        res[b].sort(key=lambda x: (x["block"], x["log_index"]))
    return res


def evaluate_vault(addr: str, key: str, blk: int, blk_ts: float, share_tx_hashes: list[str] | None = None) -> dict:
    v = c.VAULTS[key]
    a = v["address"]
    rec = {"key": key, "label": v["label"], "contract": a, "block": blk, "block_time": utc(blk_ts)}
    rec["symbol_onchain"] = c.call_string(a, "symbol()", blk)
    rec["name_onchain"] = c.call_string(a, "name()", blk)
    dec = c.call_uint(a, "decimals()", blk)
    rec["decimals"] = dec
    asset = c.call_address(a, "asset()", blk)
    rec["asset"] = asset
    rec["asset_is_verified_usdt"] = asset.lower() == USDT_ADDR
    shares = c.call_uint(a, "balanceOf(address)", blk, c._enc_addr(addr))
    rec["shares_raw"] = str(shares)
    rec["shares"] = str(c.fmt_units(shares, dec))
    rec["totalAssets_usdt"] = str(c.fmt_units(c.call_uint(a, "totalAssets()", blk), 6))
    if shares > 0:
        cta = c.call_uint(a, "convertToAssets(uint256)", blk, c._enc_uint(shares))
        rec["convertToAssets_raw"] = str(cta)
        rec["convertToAssets_usdt"] = str(c.fmt_units(cta, 6))
        try:
            pr = c.call_uint(a, "previewRedeem(uint256)", blk, c._enc_uint(shares))
            rec["previewRedeem_usdt"] = str(c.fmt_units(pr, 6))
        except Exception as e:  # noqa: BLE001
            rec["previewRedeem_error"] = str(e)[:200]
        try:
            mw = c.call_uint(a, "maxWithdraw(address)", blk, c._enc_addr(addr))
            rec["maxWithdraw_usdt"] = str(c.fmt_units(mw, 6))
        except Exception as e:  # noqa: BLE001
            rec["maxWithdraw_error"] = str(e)[:200]

    ev = fetch_vault_events(addr, a, share_tx_hashes)
    rec["events_complete"] = ev["complete"]
    rec["event_errors"] = ev["errors"]
    rec["events_source"] = ev.get("source")
    al = addr.lower()
    deps = [d for d in ev["deposits"] if d["owner"].lower() == al]
    deps_for_others = [d for d in ev["deposits"] if d["owner"].lower() != al]
    wds = [w for w in ev["withdrawals"] if w["owner"].lower() == al]
    wds_to_user_other_owner = [w for w in ev["withdrawals"] if w["owner"].lower() != al]
    rec["deposits"] = deps
    rec["deposits_paid_for_others"] = deps_for_others
    rec["withdrawals"] = wds
    rec["withdrawals_received_from_other_owner"] = wds_to_user_other_owner
    rec["share_transfers_in"] = ev["share_in"]
    rec["share_transfers_out"] = ev["share_out"]

    dep_assets = sum(d["assets_raw"] for d in deps)
    dep_shares = sum(d["shares_raw"] for d in deps)
    wd_assets = sum(w["assets_raw"] for w in wds)
    wd_shares = sum(w["shares_raw"] for w in wds)
    sh_in = sum(s["shares_raw"] for s in ev["share_in"])
    sh_out = sum(s["shares_raw"] for s in ev["share_out"])
    net_from_events = dep_shares - wd_shares + sh_in - sh_out
    rec["sum_deposits_usdt"] = str(c.fmt_units(dep_assets, 6))
    rec["sum_withdrawals_usdt"] = str(c.fmt_units(wd_assets, 6))
    rec["net_shares_from_events"] = str(c.fmt_units(net_from_events, dec))
    shares_match = net_from_events == shares
    rec["shares_match_onchain"] = shares_match
    has_transfers = bool(ev["share_in"] or ev["share_out"])
    paid_by_other = any(d["sender"].lower() != al for d in deps)
    reconstructable = ev["complete"] and shares_match and not has_transfers and not paid_by_other \
        and (deps or wds)
    rec["cost_basis_reconstructable"] = bool(reconstructable)
    reasons = []
    if not ev["complete"]:
        reasons.append("Ereignisabfrage unvollständig")
    if not shares_match:
        reasons.append("Share-Saldo aus Ereignissen weicht vom On-Chain-Saldo ab")
    if has_transfers:
        reasons.append("Vault-Anteile wurden direkt übertragen (Kostenbasis unbekannt)")
    if paid_by_other:
        reasons.append("mindestens eine Einzahlung wurde von einer anderen Adresse bezahlt")
    if not (deps or wds):
        reasons.append("keine Einzahlungs- oder Auszahlungsereignisse")
    rec["reconstruction_notes"] = reasons
    if reconstructable:
        cur = int(rec.get("convertToAssets_raw", "0"))
        gain = cur + wd_assets - dep_assets
        rec["estimated_change_usdt"] = str(c.fmt_units(gain, 6))
        rec["estimated_change_formula"] = "aktueller Gegenwert (convertToAssets) + Summe Auszahlungen − Summe Einzahlungen"
    rec["has_position"] = shares > 0
    return rec


# --------------------------------------------------------------------------- #
# Step: classification
# --------------------------------------------------------------------------- #
_profile_cache: dict = {}


def sender_profile(a: str) -> dict:
    al = a.lower()
    if al in _profile_cache:
        return _profile_cache[al]
    if len(_profile_cache) >= MAX_SENDER_PROFILES:
        return {"looked_up": False}
    p = {"looked_up": True}
    try:
        d = c.bs_get(f"/addresses/{a}")
        p["is_contract"] = bool(d.get("is_contract"))
        p["name"] = d.get("name")
        p["public_tags"] = [t.get("display_name") or t.get("label") for t in (d.get("public_tags") or [])]
        tags = (d.get("metadata") or {}).get("tags") or []
        p["metadata_tags"] = [t.get("name") for t in tags]
        p["is_scam"] = bool(d.get("is_scam"))
        p["is_verified_contract"] = bool(d.get("is_verified"))
        cnt = c.bs_get(f"/addresses/{a}/counters")
        p["token_transfers_count"] = int(cnt.get("token_transfers_count") or 0)
        p["transactions_count"] = int(cnt.get("transactions_count") or 0)
    except Exception as e:  # noqa: BLE001
        p["error"] = str(e)[:200]
    _profile_cache[al] = p
    return p


def normalize_transfers(items: list, addr: str) -> list:
    al = addr.lower()
    out = []
    for it in items:
        tok = it.get("token") or {}
        ta = (tok.get("address_hash") or tok.get("address") or "").lower()
        frm = (it.get("from") or {}).get("hash") or ""
        to = (it.get("to") or {}).get("hash") or ""
        total = it.get("total") or {}
        raw = total.get("value")
        dec = total.get("decimals") or tok.get("decimals")
        try:
            amount = c.fmt_units(int(raw), int(dec)) if raw is not None and dec not in (None, "") else None
        except Exception:  # noqa: BLE001
            amount = None
        direction = "in" if to.lower() == al and frm.lower() != al else ("out" if frm.lower() == al and to.lower() != al else "self")
        out.append({
            "timestamp": parse_ts(it["timestamp"]) if it.get("timestamp") else None,
            "block": it.get("block_number"), "tx": it.get("transaction_hash"),
            "log_index": it.get("log_index"), "from": frm, "to": to, "direction": direction,
            "token_contract": c.to_checksum(ta) if ta else None, "token_symbol_blockscout": tok.get("symbol"),
            "token_type": tok.get("type") or it.get("token_type"), "raw": raw, "decimals": dec,
            "amount": amount, "bs_type": it.get("type"), "method": it.get("method"),
            "verified_token": VERIFIED_TOKEN_ADDRS.get(ta), "vault_token": VAULT_ADDRS.get(ta),
            "from_is_contract": (it.get("from") or {}).get("is_contract"),
            "from_name": (it.get("from") or {}).get("name"),
        })
    return out


def _is_daily(ts_list: list[float]) -> tuple[float, float | None]:
    ts_list = sorted(ts_list)
    if len(ts_list) < 2:
        return 0.0, None
    iv = [(b - a) / 3600 for a, b in zip(ts_list, ts_list[1:])]
    ok = 0
    for h in iv:
        if h >= 24 - BOOST_DAILY_TOLERANCE_H:
            rem = h % 24
            if rem <= BOOST_DAILY_TOLERANCE_H or rem >= 24 - BOOST_DAILY_TOLERANCE_H:
                ok += 1
    return ok / len(iv), statistics.median(iv)


def classify(transfers: list, addr: str, vault_tx_index: dict) -> tuple[list, dict]:
    al = addr.lower()
    outgoing_to = defaultdict(list)
    for t in transfers:
        if t["direction"] == "out" and t["verified_token"]:
            outgoing_to[t["to"].lower()].append(t)

    # Sender groups for verified incoming USDT
    groups = defaultdict(list)
    for t in transfers:
        if t["direction"] == "in" and t["verified_token"] == "USDT" and t["tx"] not in vault_tx_index:
            groups[t["from"].lower()].append(t)

    boost_senders = {}
    sender_eval = {}
    for s, lst in groups.items():
        ts = [x["timestamp"] for x in lst if x["timestamp"]]
        days = {datetime.fromtimestamp(x, UTC).date() for x in ts}
        share, med = _is_daily(ts)
        maxamt = max((x["amount"] or Decimal(0)) for x in lst)
        # rolling 7-day maximum sum
        srt = sorted(lst, key=lambda x: x["timestamp"] or 0)
        roll_max = Decimal(0)
        for i, x in enumerate(srt):
            win = sum((y["amount"] or Decimal(0)) for y in srt[i:] if (y["timestamp"] - x["timestamp"]) < 7 * 86400)
            roll_max = max(roll_max, win)
        reciprocal = s in outgoing_to
        ev = {"sender": c.to_checksum(s) if s else s, "n": len(lst), "distinct_days": len(days),
              "regular_share": round(share, 2), "median_interval_h": round(med, 1) if med else None,
              "max_single": str(maxamt), "max_rolling_7d": str(roll_max), "user_sent_to_sender": reciprocal}
        pattern = (len(lst) >= BOOST_MIN_TRANSFERS and len(days) >= BOOST_MIN_DISTINCT_DAYS
                   and share >= BOOST_MIN_REGULAR_SHARE and maxamt <= BOOST_MAX_SINGLE_USDT and not reciprocal)
        ev["pattern_match"] = pattern
        if pattern:
            prof = sender_profile(s)
            ev["profile"] = prof
            distributor = prof.get("token_transfers_count", 0) >= BOOST_DISTRIBUTOR_MIN_TRANSFERS
            ev["distributor_profile"] = distributor
            if distributor and not prof.get("is_scam"):
                boost_senders[s] = ev
        sender_eval[s] = ev

    rows = []
    for t in transfers:
        r = dict(t)
        reason = ""
        conf = ""
        if not (t["verified_token"] or t["vault_token"]):
            cat, conf = CAT_UNVERIFIED, "–"
            reason = ("Tokenvertrag gehört nicht zu den konfigurierten, on-chain verifizierten Verträgen; "
                      "gleich aussehende Namen/Symbole begründen keine Echtheit.")
        elif t["vault_token"]:
            cat, conf = CAT_VAULT_SHARE, "hoch (Vault-Vertrag)"
            reason = f"Transfer von Anteilen des Vaults {t['vault_token']} ({t['bs_type']})."
        elif t["tx"] in vault_tx_index and t["verified_token"] == "USDT":
            kind = vault_tx_index[t["tx"]]
            if t["direction"] == "out" and "deposit" in kind:
                cat, conf = CAT_VAULT_IN, "hoch (Deposit-Event)"
                reason = f"Gleiche Transaktion enthält ein ERC-4626-Deposit-Event des Vaults {kind['deposit']} für diese Adresse."
            elif t["direction"] == "in" and "withdraw" in kind:
                cat, conf = CAT_VAULT_OUT, "hoch (Withdraw-Event)"
                reason = f"Gleiche Transaktion enthält ein ERC-4626-Withdraw-Event des Vaults {kind['withdraw']} zugunsten dieser Adresse."
            else:
                cat, conf = (CAT_OUTGOING if t["direction"] == "out" else CAT_UNKNOWN), "niedrig"
                reason = "USDT-Bewegung in einer Vault-Transaktion, Richtung passt nicht eindeutig zu Deposit/Withdraw."
        elif t["direction"] == "out":
            cat, conf = CAT_OUTGOING, "–"
            reason = "Ausgehender Transfer der beobachteten Adresse."
        elif t["direction"] == "self":
            cat, conf = "Eigenübertrag", "–"
            reason = "Absender und Empfänger identisch."
        else:
            s = t["from"].lower()
            if t["verified_token"] == "USDT" and s in boost_senders:
                ev = boost_senders[s]
                cat, conf = CAT_BOOST, "Annahme (Muster), nicht offiziell bestätigt"
                reason = (f"Absender sendet regelmäßig im ~24-h-Takt ({ev['n']} Eingänge an {ev['distinct_days']} Tagen, "
                          f"Regelmäßigkeit {int(ev['regular_share']*100)} %), Einzelbeträge ≤ {BOOST_MAX_SINGLE_USDT} USDT, "
                          f"keine Rückzahlungen an den Absender, Absender ist Massenauszahler "
                          f"({ev['profile'].get('token_transfers_count')} Token-Transfers). "
                          "Kein offiziell veröffentlichter Boost-Auszahler on-chain verifiziert.")
            else:
                refund = None
                if t["amount"] is not None:
                    for o in outgoing_to.get(s, []):
                        if o["token_contract"] == t["token_contract"] and o["timestamp"] and t["timestamp"] \
                                and 0 < t["timestamp"] - o["timestamp"] <= 30 * 86400 and o["amount"] \
                                and abs(o["amount"] - t["amount"]) <= o["amount"] * Decimal("0.01"):
                            refund = o
                            break
                prof = sender_profile(t["from"]) if t["from"] else {}
                if refund:
                    cat, conf = CAT_REFUND, "niedrig"
                    reason = f"Betrag entspricht (±1 %) einem früheren Ausgang an denselben Absender (Tx {refund['tx'][:10]}…)."
                elif prof.get("is_contract") or prof.get("name") or prof.get("public_tags") or \
                        prof.get("token_transfers_count", 0) >= BOOST_DISTRIBUTOR_MIN_TRANSFERS:
                    cat, conf = CAT_RAMP, "niedrig"
                    bits = []
                    if prof.get("is_contract"):
                        bits.append("Absender ist ein Smart Contract")
                    if prof.get("name"):
                        bits.append(f"Blockscout-Name „{prof['name']}“ (Drittangabe)")
                    if prof.get("public_tags"):
                        bits.append(f"Blockscout-Tags {prof['public_tags']} (Drittangabe)")
                    if prof.get("token_transfers_count", 0) >= BOOST_DISTRIBUTOR_MIN_TRANSFERS:
                        bits.append(f"Absender mit sehr vielen Transfers ({prof['token_transfers_count']}), aber ohne Boost-Muster")
                    reason = "; ".join(bits) + "."
                elif prof.get("looked_up") and not prof.get("is_contract") and \
                        (s in outgoing_to or prof.get("token_transfers_count", 0) < 5_000):
                    cat, conf = CAT_P2P, "niedrig bis mittel"
                    reason = ("Absender ist eine gewöhnliche Adresse (EOA) mit geringem Transfervolumen"
                              + (" und die Wallet hat zuvor an diese Adresse gesendet." if s in outgoing_to else "."))
                else:
                    cat, conf = CAT_UNKNOWN, "–"
                    reason = "Keine belastbaren Merkmale für eine Zuordnung."
        r.update({"category": cat, "confidence": conf, "reason": reason})
        rows.append(r)
    return rows, {"sender_eval": sender_eval, "boost_senders": list(boost_senders)}


# --------------------------------------------------------------------------- #
# Report rendering
# --------------------------------------------------------------------------- #
def boost_summary(rows: list, ref_ts: float, history_start: float | None) -> dict:
    b = [r for r in rows if r["category"] == CAT_BOOST]
    out = {}
    for label, secs in (("24 Stunden", 86400), ("7 Tage", 7 * 86400), ("30 Tage", 30 * 86400), ("Gesamt (abgefragter Verlauf)", None)):
        sel = [r for r in b if secs is None or (ref_ts - r["timestamp"]) <= secs]
        out[label] = {"count": len(sel), "sum": sum(((r["amount"] or Decimal(0)) for r in sel), Decimal(0)),
                      "first": utc(min(r["timestamp"] for r in sel)) if sel else None,
                      "last": utc(max(r["timestamp"] for r in sel)) if sel else None}
    return out


def render_md(ctx: dict) -> str:
    L = []
    w = ctx["wallet"]
    L.append("# MiniPay-Wallet: Nur-Lese-Bericht (Celo Mainnet)\n")
    L.append("| Feld | Wert |\n|---|---|")
    L.append(f"| Abfragezeitpunkt (UTC) | {ctx['queried_at']} |")
    L.append("| Netzwerk | Celo Mainnet |")
    L.append(f"| Chain-ID (on-chain geprüft) | {ctx['chain_id']} |")
    L.append(f"| Bestätigte Wallet-Adresse (gekürzt) | `{short(w)}` |")
    L.append(f"| Referenzblock | [{ctx['block']}]({c.EXPLORER}/block/{ctx['block']}) ({ctx['block_time']}) |")
    L.append(f"| Betrachteter Zeitraum der Historie | {ctx['window_label']} |")
    L.append("| Modus | Nur lesend: keine Signatur, keine Transaktion, keine Wallet-Verbindung |\n")
    L.append("> **Kennzeichnung:** Alle Beträge sind **On-Chain-Beobachtungen** auf Celo Mainnet. Ein Eintrag auf der "
             "Blockchain allein beweist nicht, dass er von MiniPay, Opera oder einem bestimmten Programm stammt.\n")

    # 1 Balances
    L.append("## 1. Bestände zum Referenzblock\n")
    n = ctx["balances"]["native"]
    L.append("### 1.1 Nativer CELO-Bestand\n")
    L.append("| Asset | Bestand | Rohwert (wei) | Dezimalstellen | Methode | Block |\n|---|---:|---:|---:|---|---:|")
    L.append(f"| CELO | {dfmt(Decimal(n['formatted']), 6)} | {n['raw']} | 18 | eth_getBalance | {n['block']} |\n")
    L.append("### 1.2 Verifizierte Stablecoin-Bestände\n")
    L.append("| Asset | On-Chain-Symbol | Vertrag | Dezimalstellen (on-chain/erwartet) | Metadaten verifiziert | Bestand | Rohwert |\n|---|---|---|---|---|---:|---:|")
    usd_sum = Decimal(0)
    for k, t in ctx["balances"]["tokens"].items():
        if "error" in t:
            L.append(f"| {k} | – | [{short(t['contract'])}]({c.addr_link(t['contract'])}) | – | Fehler | – | {t['error'][:80]} |")
            continue
        ok = "ja" if t["metadata_verified"] else "**nein – nicht gezählt**"
        L.append(f"| {k} | {t['symbol_onchain']} | [{short(t['contract'])}]({c.addr_link(t['contract'])}) | "
                 f"{t['decimals_onchain']}/{t['decimals_expected']} | {ok} | {dfmt(Decimal(t['formatted']), 6)} | {t['raw']} |")
        if t["metadata_verified"] and k in ("USDT", "USDC", "USDm"):
            usd_sum += Decimal(t["formatted"])
    eur = ctx["balances"]["tokens"].get("EURm", {})
    L.append("")
    L.append(f"**Summe verifizierter USD-Stablecoins (USDT + USDC + USDm, nominal 1:1, ohne Kursumrechnung):** "
             f"{dfmt(usd_sum, 6)}. EURm wird getrennt geführt ({dfmt(Decimal(eur.get('formatted', '0')), 6)} EURm) und "
             "nicht in USD umgerechnet. Vault-Positionen sind in dieser Summe nicht enthalten (siehe Abschnitt 2).\n")

    L.append("### 1.3 Weitere Token (unverifiziert, nicht in Summen)\n")
    others = ctx["other_tokens"]
    if others:
        L.append("> Token mit gleich aussehenden Namen, Symbolen oder unerwarteten Contract-Adressen gelten **nicht** als echte "
                 "Guthaben. Sie werden nur zur Transparenz aufgeführt. Nicht damit interagieren.\n")
        L.append("| Name | Symbol | Typ | Vertrag | Bestand (laut Blockscout) | Auffälligkeit |\n|---|---|---|---|---:|---|")
        for o in others:
            flags = []
            if o["lookalike_symbol"]:
                flags.append("ähnelt bekanntem Asset")
            if o["blockscout_is_scam"]:
                flags.append("Blockscout: Scam-Markierung")
            L.append(f"| {o['name'] or '–'} | {o['symbol'] or '–'} | {o['type'] or '–'} | "
                     f"[{short(o['contract'] or '')}]({c.addr_link(o['contract'] or '')}) | {o['formatted']} | "
                     f"{', '.join(flags) or 'unverifiziert'} |")
        L.append("")
    else:
        L.append("Keine weiteren Token laut Blockscout.\n")

    # 2 Earn
    L.append("## 2. MiniPay Earn: geschätzte Vault-Positionen\n")
    L.append("> MiniPay Earn ist ein **separates DeFi-Angebot** (Drittanbieter-Strategien über ERC-4626-Vaults) und nicht dasselbe "
             "wie die tägliche Boost-Ausschüttung. Vertrags- oder Tokennamen sind keine Sicherheitsgarantie.\n")
    any_pos = False
    L.append("| Vault | Vertrag | Basisanlage (asset()) | Gehaltene Shares | Gegenwert convertToAssets (USDT) | previewRedeem (USDT) | maxWithdraw (USDT) | Block |\n|---|---|---|---:|---:|---:|---:|---:|")
    for v in ctx["vaults"]:
        any_pos |= v["has_position"]
        asset_lbl = "USDT (verifiziert)" if v["asset_is_verified_usdt"] else f"**abweichend: {v['asset']}**"
        L.append(f"| {v['symbol_onchain']} ({v['label']}) | [{short(v['contract'])}]({c.addr_link(v['contract'])}) | {asset_lbl} | "
                 f"{dfmt(Decimal(v['shares']), 6)} | {dfmt(Decimal(v.get('convertToAssets_usdt', '0')), 6)} | "
                 f"{dfmt(Decimal(v['previewRedeem_usdt']), 6) if v.get('previewRedeem_usdt') else '–'} | "
                 f"{dfmt(Decimal(v['maxWithdraw_usdt']), 6) if v.get('maxWithdraw_usdt') else '–'} | {v['block']} |")
    L.append("")
    if not any_pos:
        L.append("**Keine erkennbare Position in den geprüften MiniPay-Earn-Vaults** zum Referenzblock.\n")
    L.append(f"Abfragezeitpunkt der Vault-Werte: {ctx['block_time']}, Block {ctx['block']}. Der geschätzte Gegenwert kann sich "
             "bis zu einer tatsächlichen Rückgabe ändern (Zinsentwicklung, Gebühren, Liquidität der zugrunde liegenden Protokolle).\n")

    L.append("### 2.1 Erkannte Einzahlungen und Auszahlungen (Deposit-/Withdraw-Ereignisse)\n")
    any_ev = False
    for v in ctx["vaults"]:
        evs = [("Deposit", d) for d in v["deposits"]] + [("Withdraw", w) for w in v["withdrawals"]]
        evs += [("Deposit für andere Adresse", d) for d in v["deposits_paid_for_others"]]
        evs += [("Withdraw aus fremder Position an diese Adresse", w) for w in v["withdrawals_received_from_other_owner"]]
        if not evs and not v["share_transfers_in"] and not v["share_transfers_out"]:
            continue
        any_ev = True
        L.append(f"**{v['symbol_onchain']}**\n")
        L.append("| Datum/Uhrzeit (UTC) | Vorgang | USDT | Shares | Block | Transaktion |\n|---|---|---:|---:|---:|---|")
        for kind, e in sorted(evs, key=lambda x: x[1]["block"]):
            L.append(f"| {utc(e['timestamp'])} | {kind} | {dfmt(c.fmt_units(e['assets_raw'], 6))} | "
                     f"{dfmt(c.fmt_units(e['shares_raw'], v['decimals']))} | {e['block']} | [{e['tx'][:10]}…]({c.tx_link(e['tx'])}) |")
        for kind, lst in (("Shares empfangen", v["share_transfers_in"]), ("Shares gesendet", v["share_transfers_out"])):
            for e in lst:
                L.append(f"| {utc(e['timestamp'])} | {kind} | – | {dfmt(c.fmt_units(e['shares_raw'], v['decimals']))} | "
                         f"{e['block']} | [{e['tx'][:10]}…]({c.tx_link(e['tx'])}) |")
        L.append("")
        L.append(f"- Summe Einzahlungen: {dfmt(Decimal(v['sum_deposits_usdt']))} USDT · Summe Auszahlungen: "
                 f"{dfmt(Decimal(v['sum_withdrawals_usdt']))} USDT · Share-Saldo aus Ereignissen: {dfmt(Decimal(v['net_shares_from_events']))} "
                 f"(on-chain: {dfmt(Decimal(v['shares']))}, {'übereinstimmend' if v['shares_match_onchain'] else 'ABWEICHEND'})")
        if v["cost_basis_reconstructable"]:
            L.append(f"- **Geschätzte Wertveränderung:** {dfmt(Decimal(v['estimated_change_usdt']))} USDT "
                     f"({v['estimated_change_formula']}). Schätzung, kein realisierter Gewinn.")
        else:
            L.append("- Wertveränderung **nicht zuverlässig rekonstruierbar**: " + "; ".join(v["reconstruction_notes"]) + ".")
        L.append("")
    if not any_ev:
        L.append("Keine Deposit-, Withdraw-, Mint- oder Redeem-Ereignisse dieser Adresse in den geprüften Vaults gefunden "
                 "(Mint/Redeem erzeugen nach ERC-4626 ebenfalls Deposit-/Withdraw-Ereignisse).\n")

    # 3 Incoming
    rows = ctx["rows"]
    inc = [r for r in rows if r["direction"] == "in"]
    inc_native = ctx["native_incoming"]
    L.append("## 3. Eingehende Werte: Transaktionsübersicht\n")
    L.append(f"Quelle: Celo-Blockscout-API v2 (`/addresses/…/token-transfers`, `/transactions`, `/internal-transactions`), "
             f"Seiten abgerufen: {ctx['tt_meta']['pages']}, vollständig im Zeitraum: {'ja' if ctx['tt_meta']['complete'] else '**nein**'}.\n")
    cat_tot = defaultdict(lambda: [0, Decimal(0)])
    for r in inc:
        if r["verified_token"] == "USDT":
            cat_tot[r["category"]][0] += 1
            cat_tot[r["category"]][1] += r["amount"] or Decimal(0)
    L.append("### 3.1 Bestätigte USDT-Eingänge nach Kategorie (verifizierter USDT-Vertrag)\n")
    L.append("| Kategorie | Anzahl | Summe USDT |\n|---|---:|---:|")
    for k, (n_, s_) in sorted(cat_tot.items(), key=lambda x: -x[1][1]):
        L.append(f"| {k} | {n_} | {dfmt(s_)} |")
    if not cat_tot:
        L.append("| – | 0 | 0 |")
    L.append("\n„Bestätigt“ bedeutet hier nur: Der Transfer stammt vom verifizierten USDT-Vertrag und ist on-chain eingetragen. "
             "Die Herkunft (Kategorie) ist davon getrennt zu bewerten.\n")
    L.append("### 3.2 Einzelaufstellung eingehender Token-Transfers\n")
    show = sorted(inc, key=lambda r: -(r["timestamp"] or 0))
    limit = 400
    if len(show) > limit:
        L.append(f"Es werden die {limit} jüngsten von {len(show)} Eingängen gezeigt; die vollständige Liste steht in der CSV-Datei.\n")
    L.append("| Datum/Uhrzeit (UTC) | Betrag | Asset | Absender | Kategorie | Sicherheit der Zuordnung | Begründung | Explorer |\n|---|---:|---|---|---|---|---|---|")
    for r in show[:limit]:
        asset = r["verified_token"] or r["vault_token"] or f"{r['token_symbol_blockscout'] or '?'} (unverifiziert)"
        amt = dfmt(r["amount"]) if r["amount"] is not None else (r["raw"] or "–")
        L.append(f"| {utc(r['timestamp']) if r['timestamp'] else '–'} | {amt} | {asset} | "
                 f"[{short(r['from'])}]({c.addr_link(r['from'])}) | {r['category']} | {r['confidence']} | {r['reason']} | "
                 f"[{(r['tx'] or '')[:10]}…]({c.tx_link(r['tx'])}) |")
    L.append("")
    L.append("### 3.3 Eingehende native CELO-Beträge\n")
    if inc_native:
        L.append("| Datum/Uhrzeit (UTC) | Betrag CELO | Art | Absender | Explorer |\n|---|---:|---|---|---|")
        for t in sorted(inc_native, key=lambda x: x["timestamp"], reverse=True)[:200]:
            L.append(f"| {utc(parse_ts(t['timestamp']))} | {dfmt(c.fmt_units(int(t['raw']), 18))} | {t['kind']} | "
                     f"[{short(t['from'] or '')}]({c.addr_link(t['from'] or '')}) | [{t['tx'][:10]}…]({c.tx_link(t['tx'])}) |")
        L.append("")
    else:
        L.append("Keine eingehenden nativen CELO-Beträge im Zeitraum.\n")

    # 4 Boost
    L.append("## 4. Mögliche MiniPay-Boost-Erträge (Annahme)\n")
    L.append("| Zeitraum (bis Referenzblock) | Anzahl | Summe USDT | Erster | Letzter |\n|---|---:|---:|---|---|")
    for k, v in ctx["boost"].items():
        L.append(f"| {k} | {v['count']} | {dfmt(v['sum'])} | {v['first'] or '–'} | {v['last'] or '–'} |")
    L.append("")
    bs = ctx["class_meta"]["boost_senders"]
    if bs:
        L.append("Als mögliche Auszahler erkannte Absender (Muster, **nicht offiziell bestätigt**): " +
                 ", ".join(f"[{short(c.to_checksum(s))}]({c.addr_link(s)})" for s in bs) + ".\n")
    L.append("> **Annahme-Kennzeichnung:** Für MiniPay Boost ist kein offizieller Auszahler on-chain verifiziert oder öffentlich dokumentiert. "
             "Alle hier zusammengefassten Beträge sind deshalb „möglicher MiniPay-Boost-Ertrag – nicht abschließend zuordenbar“. "
             "Derselbe Absender kann auch andere MiniPay-Aktionen auszahlen, z. B. Kampagnen, Empfehlungs- oder Aufgabenprämien.\n")
    L.append("Einordnung: Nach den [Boost-Bedingungen](https://minipay.to/minipay-boost-terms-conditions) beträgt die Belohnung **bis zu** "
             "2 % pro Woche auf USDT, höchstens 10 USDT pro Woche (außer bei Kampagnen), bei mindestens 1 USDT Bestand. Sie wird wöchentlich "
             "berechnet und täglich ausgeschüttet. Das ist **kein garantierter Satz**: Stufen, Nutzung und Programmänderungen beeinflussen den "
             "tatsächlichen Betrag. Ein Vergleich der beobachteten Summen mit dem Maximum ist deshalb kein Anspruchsnachweis.\n")

    # 5 Classification rules / gaps
    L.append("## 5. Methodik, Datenlücken und Annahmen\n")
    L.append("**Klassifikationsregeln (für jede Zeile ist die Begründung angegeben):**\n")
    L.append(f"- *{CAT_BOOST}*: USDT-Eingänge eines Absenders mit mindestens {BOOST_MIN_TRANSFERS} Eingängen an mindestens "
             f"{BOOST_MIN_DISTINCT_DAYS} Tagen, mindestens {int(BOOST_MIN_REGULAR_SHARE*100)} % der Abstände im ~24-h-Raster "
             f"(±{BOOST_DAILY_TOLERANCE_H} h), Einzelbeträge ≤ {BOOST_MAX_SINGLE_USDT} USDT, keine Ausgänge der Wallet an diesen Absender, Absender mit "
             f"≥ {BOOST_DISTRIBUTOR_MIN_TRANSFERS:,} Token-Transfers (Massenauszahler).")
    L.append(f"- *{CAT_VAULT_IN}* / *{CAT_VAULT_OUT}*: USDT-Bewegung in einer Transaktion mit ERC-4626-Deposit- bzw. Withdraw-Event der geprüften Vaults für diese Adresse.")
    L.append(f"- *{CAT_REFUND}*: Betrag entspricht (±1 %) einem früheren Ausgang an denselben Absender innerhalb von 30 Tagen.")
    L.append(f"- *{CAT_RAMP}*: Absender ist ein Smart Contract, hat einen Blockscout-Namen oder -Tag (Drittangabe) oder ist ein Massenabsender ohne Boost-Muster.")
    L.append(f"- *{CAT_P2P}*: Absender ist eine gewöhnliche Adresse mit geringem Transfervolumen oder hat zuvor Zahlungen von dieser Wallet erhalten.")
    L.append(f"- *{CAT_UNKNOWN}*: keine belastbaren Merkmale. *{CAT_UNVERIFIED}*: Token außerhalb der verifizierten Verträge.\n")
    L.append("**Datenlücken, Fehler und Hinweise:**\n")
    for g in ctx["gaps"]:
        L.append(f"- {g}")
    L.append("")
    L.append("## 6. Risiken\n")
    L.append("- **MiniPay Earn** umfasst Drittanbieter- und DeFi-Risiken, etwa Smart-Contract-, Protokoll-, Liquiditäts-, Oracle- und Stablecoin-Risiken "
             "(Aave V3, Morpho/Feather, Vault-Betreiber). Vergangene Renditen sind keine Zusage. Der Gegenwert ist eine Schätzung zum Referenzblock.")
    L.append("- **MiniPay Boost** ist ein freiwilliges Prämienprogramm, das jederzeit geändert, ausgesetzt oder beendet werden kann.")
    L.append("- **Unverifizierte Token** können Betrugsversuche sein (z. B. gefälschte USDT-Kopien). Nicht damit interagieren.")
    L.append("- **Stablecoins** können ihre Bindung verlieren. Hier wird nominal 1:1 und ohne Kursbewertung gerechnet.\n")
    L.append("## 7. Datenschutz\n")
    L.append("Alle Celo-Mainnet-Daten dieser Adresse sind öffentlich einsehbar: Bestände, Transfers und Gegenparteien. Die Zuordnung der Adresse zu einer "
             "Person oder einem Manus-Account ist **datenschutzrelevant**, denn wer die Zuordnung kennt, kann die gesamte Finanzhistorie dieser Adresse verfolgen. "
             "Dieser Bericht enthält Explorer-Links, aus denen die vollständige Adresse ableitbar ist. Bitte nur bewusst teilen.\n")
    L.append("## 8. Nachweis des Nur-Lese-Betriebs\n")
    L.append("| Zugriff | Anzahl |\n|---|---:|")
    for k, v in sorted(c.AUDIT["rpc"].items()):
        L.append(f"| RPC `{k}` (forno.celo.org) | {v} |")
    for k, v in sorted(c.AUDIT["http_get"].items()):
        L.append(f"| HTTP GET {k} | {v} |")
    L.append("")
    L.append("Es wurden keine Signaturen angefordert, keine Transaktionen erzeugt oder gesendet und keine Wallet-Verbindung hergestellt. "
             "Geheime Daten (Passwörter, private Schlüssel, Seed- oder Wiederherstellungsphrasen, SMS- oder 2FA-Codes) wurden weder angefordert noch verarbeitet. "
             "Jede künftige Aktion mit echten Vermögenswerten ist ein neuer, schreibender Vorgang. Er wird vorher mit Betrag, Ziel, Gebühren, "
             "Risiken und Konsequenzen beschrieben und muss von Ihnen ausdrücklich freigegeben und in Ihrer eigenen Wallet bestätigt werden.\n")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Main commands
# --------------------------------------------------------------------------- #
def cmd_validate(address: str) -> int:
    v = c.validate_address(address)
    print(json.dumps(v, ensure_ascii=False, indent=2))
    return 0 if v["valid"] else 2


def cmd_report(address: str, confirmed: bool, days: int | None, out_dir: str) -> int:
    v = c.validate_address(address)
    if not v["valid"]:
        print("STOP: Adresse ungültig:", "; ".join(v["checks"]))
        return 2
    if not confirmed:
        print(f"STOP: Adresse {v['short']} wurde noch nicht bestätigt (Flag --confirmed fehlt).")
        return 3
    addr = v["checksum"]
    queried_at = datetime.now(UTC)
    cid = c.chain_id()
    if cid != c.EXPECTED_CHAIN_ID:
        print(f"STOP: Chain-ID {cid} ≠ {c.EXPECTED_CHAIN_ID} (Celo Mainnet).")
        return 4
    blk = c.block_number()
    blk_ts = int(c.get_block(blk)["timestamp"], 16)
    gaps = []

    code = c.get_code(addr, blk)
    if code not in ("0x", "0x0", None):
        gaps.append("Die Adresse enthält Smart-Contract-Code (für eine MiniPay-Wallet ungewöhnlich). Bitte Adresse prüfen.")
    try:
        counters = c.bs_get(f"/addresses/{addr}/counters")
    except Exception as e:  # noqa: BLE001
        counters = {}
        gaps.append(f"Blockscout-Zähler nicht abrufbar: {e}")
    balances = read_balances(addr, blk)
    has_activity = int(counters.get("transactions_count") or 0) > 0 or int(counters.get("token_transfers_count") or 0) > 0 \
        or int(balances["native"]["raw"]) > 0 or any(int(t.get("raw") or 0) > 0 for t in balances["tokens"].values())
    if not has_activity and counters:
        print(f"STOP: Für {v['short']} gibt es auf Celo Mainnet keinerlei Aktivität oder Bestände. "
              "Bitte prüfen Sie, ob es sich um Ihre MiniPay-Adresse auf Celo handelt.")
        return 5

    since_ts = (blk_ts - days * 86400) if days else None
    window_label = f"letzte {days} Tage bis Referenzblock" if days else "gesamter von Blockscout verfügbarer Verlauf"

    other_tokens, errs = read_other_tokens(addr)
    gaps += errs
    tt_items, tt_meta = fetch_token_transfers(addr, since_ts)
    if not tt_meta["complete"]:
        gaps.append(f"Token-Transferhistorie nach {tt_meta['pages']} Seiten begrenzt – ältere Einträge fehlen.")
    native_in, native_meta = fetch_native_incoming(addr, since_ts)
    for k, m in native_meta.items():
        if not m["complete"]:
            gaps.append(f"Native-CELO-Historie ({k}) begrenzt nach {m['pages']} Seiten.")

    share_txs = defaultdict(list)
    for it in tt_items:
        ta = ((it.get("token") or {}).get("address_hash") or "").lower()
        if ta in VAULT_ADDRS and it.get("transaction_hash"):
            share_txs[VAULT_ADDRS[ta]].append(it["transaction_hash"])
    vaults = [evaluate_vault(addr, k, blk, blk_ts, share_txs.get(k, [])) for k in c.VAULTS]
    vault_tx_index = defaultdict(dict)
    for vr in vaults:
        for d in vr["deposits"] + vr["deposits_paid_for_others"]:
            vault_tx_index[d["tx"]]["deposit"] = vr["key"]
        for w in vr["withdrawals"] + vr["withdrawals_received_from_other_owner"]:
            vault_tx_index[w["tx"]]["withdraw"] = vr["key"]
        if not vr["events_complete"]:
            gaps.append(f"Vault-Ereignisse {vr['key']}: möglicherweise unvollständig. Quelle: {vr['events_source']}. "
                        f"Hinweise: {'; '.join(str(e) for e in vr['event_errors'][:3])}")

    transfers = normalize_transfers(tt_items, addr)
    # Exclude anything newer than the reference block for consistency
    transfers = [t for t in transfers if t["block"] is None or t["block"] <= blk]
    rows, class_meta = classify(transfers, addr, vault_tx_index)
    boost = boost_summary(rows, blk_ts, since_ts)

    unver_tx = sum(1 for r in rows if r["category"] == CAT_UNVERIFIED)
    if unver_tx:
        gaps.append(f"{unver_tx} Transfers unverifizierter Token wurden erkannt und aus allen Summen ausgeschlossen.")
    if len(_profile_cache) >= MAX_SENDER_PROFILES:
        gaps.append(f"Absenderprofile auf {MAX_SENDER_PROFILES} begrenzt; weitere Absender ohne Profil wurden als „unbekannt“ geführt.")
    gaps.append("Für MiniPay Boost ist kein offizieller Auszahler on-chain verifiziert oder öffentlich dokumentiert; Boost-Zuordnungen sind Annahmen.")
    gaps.append("Historische Bestände zu früheren Blöcken wurden nicht rekonstruiert. Eine effektive Boost-Rendite pro Woche wird deshalb nicht berechnet.")
    gaps.append("Gasgebühren, die MiniPay in Stablecoins zahlt (Celo Fee Abstraction), erscheinen nicht zwingend als Token-Transfer. Der Bericht rekonstruiert keine Salden aus Transfers.")
    gaps.append("Blockscout-Namen und -Tags sind Drittangaben und gelten nicht als offizielle Verifizierung.")
    gaps.append("Weitere, hier nicht konfigurierte Earn-Vaults oder Strategien werden nicht erfasst. Geprüft wurden nur mpAaveUSDT und mpFeatherUSDT.")
    gaps.append("Transfers nach dem Referenzblock bleiben unberücksichtigt, damit Bestände und Historie konsistent sind.")

    ctx = {"wallet": addr, "queried_at": queried_at.strftime("%Y-%m-%d %H:%M:%S UTC"), "chain_id": cid,
           "block": blk, "block_time": utc(blk_ts), "window_label": window_label, "balances": balances,
           "other_tokens": other_tokens, "vaults": vaults, "rows": rows, "native_incoming": native_in,
           "tt_meta": tt_meta, "boost": boost, "class_meta": class_meta, "gaps": gaps}

    os.makedirs(out_dir, exist_ok=True)
    stamp = queried_at.strftime("%Y%m%dT%H%M%SZ")
    md_path = os.path.join(out_dir, f"minipay_bericht_{stamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_md(ctx))
    csv_path = os.path.join(out_dir, f"minipay_transfers_{stamp}.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["zeit_utc", "block", "tx_hash", "explorer", "richtung", "absender", "empfaenger", "token_vertrag",
                      "asset", "rohbetrag", "dezimalstellen", "betrag", "kategorie", "sicherheit", "begruendung"])
        for r in sorted(rows, key=lambda r: r["timestamp"] or 0):
            wtr.writerow([utc(r["timestamp"]) if r["timestamp"] else "", r["block"], r["tx"], c.tx_link(r["tx"]),
                          r["direction"], r["from"], r["to"], r["token_contract"],
                          r["verified_token"] or r["vault_token"] or f"{r['token_symbol_blockscout']} (unverifiziert)",
                          r["raw"], r["decimals"], str(r["amount"]) if r["amount"] is not None else "",
                          r["category"], r["confidence"], r["reason"]])
    json_path = os.path.join(out_dir, f"minipay_daten_{stamp}.json")

    def _ser(o):
        if isinstance(o, Decimal):
            return str(o)
        return str(o)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in ctx.items()} | {"audit": c.AUDIT}, f, ensure_ascii=False, indent=1, default=_ser)
    print(json.dumps({"md": md_path, "csv": csv_path, "json": json_path, "audit": c.AUDIT,
                      "boost": {k: {"count": v["count"], "sum": str(v["sum"])} for k, v in boost.items()},
                      "transfers": len(rows), "gaps": len(gaps)}, ensure_ascii=False, indent=2))
    return 0


def cmd_bind(address: str, consent: bool, label: str, path: str) -> int:
    v = c.validate_address(address)
    if not v["valid"]:
        print("STOP: Adresse ungültig")
        return 2
    if not consent:
        print("STOP: Ohne ausdrückliche Zustimmung (--consent) wird keine Zuordnung gespeichert.")
        return 3
    rec = {"public_address": v["checksum"], "network": "Celo Mainnet", "chain_id": c.EXPECTED_CHAIN_ID,
           "account_label": label, "consent_recorded_utc": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
           "scope": "read-only monitoring, evaluation and reporting",
           "write_actions_allowed": False, "secrets_stored": False,
           "note": "Eine öffentliche Adresse berechtigt niemals zu Transaktionen. Jede Aktion mit Vermögenswerten erfordert eine neue, separate Freigabe."}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("validate")
    p1.add_argument("address")
    p2 = sub.add_parser("report")
    p2.add_argument("address")
    p2.add_argument("--confirmed", action="store_true")
    p2.add_argument("--days", type=int, default=None)
    p2.add_argument("--out", default="reports")
    p3 = sub.add_parser("bind")
    p3.add_argument("address")
    p3.add_argument("--consent", action="store_true")
    p3.add_argument("--account-label", required=True)
    p3.add_argument("--path", default="wallet_binding.json")
    a = ap.parse_args()
    if a.cmd == "validate":
        return cmd_validate(a.address)
    if a.cmd == "report":
        return cmd_report(a.address, a.confirmed, a.days, a.out)
    return cmd_bind(a.address, a.consent, a.account_label, a.path)


if __name__ == "__main__":
    sys.exit(main())
