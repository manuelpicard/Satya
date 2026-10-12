"""
verify_contracts.py - address-independent verification of the configured
Celo Mainnet token and MiniPay Earn vault contracts. No wallet data involved.
Output: contract_verification.json
"""
import json
from datetime import datetime, timezone

import celo_readonly as c

out = {"queried_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
cid = c.chain_id()
out["chain_id"] = cid
if cid != c.EXPECTED_CHAIN_ID:
    raise SystemExit(f"STOP: Chain-ID {cid} ist nicht Celo Mainnet ({c.EXPECTED_CHAIN_ID})")
blk = c.block_number()
b = c.get_block(blk)
out["reference_block"] = blk
out["reference_block_time_utc"] = datetime.fromtimestamp(int(b["timestamp"], 16), timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

tokens = {}
for key, t in c.TOKENS.items():
    a = t["address"]
    rec = {"address": a, "checksum_ok": c.to_checksum(a) == a}
    code = c.get_code(a, blk)
    rec["has_code"] = code not in ("0x", "0x0", None)
    rec["name"] = c.call_string(a, "name()", blk)
    rec["symbol"] = c.call_string(a, "symbol()", blk)
    rec["decimals"] = c.call_uint(a, "decimals()", blk)
    rec["decimals_expected"] = t["decimals"]
    rec["decimals_ok"] = rec["decimals"] == t["decimals"]
    rec["symbol_ok"] = rec["symbol"] in t["expected_symbols"]
    try:
        meta = c.bs_get(f"/tokens/{a}")
        rec["blockscout_token_name"] = meta.get("name")
        rec["blockscout_symbol"] = meta.get("symbol")
        rec["blockscout_type"] = meta.get("type")
        rec["blockscout_holders"] = meta.get("holders_count") or meta.get("holders")
    except Exception as e:  # noqa: BLE001
        rec["blockscout_error"] = str(e)
    try:
        sc = c.bs_get(f"/smart-contracts/{a}")
        rec["blockscout_verified_source"] = bool(sc.get("is_verified")) or bool(sc.get("source_code"))
        rec["blockscout_contract_name"] = sc.get("name")
    except Exception as e:  # noqa: BLE001
        rec["blockscout_verified_source"] = None
        rec["blockscout_sc_error"] = str(e)[:200]
    rec["verified"] = rec["has_code"] and rec["decimals_ok"] and rec["symbol_ok"] and rec["checksum_ok"]
    tokens[key] = rec
out["tokens"] = tokens

usdt = c.TOKENS["USDT"]["address"].lower()
vaults = {}
for key, v in c.VAULTS.items():
    a = v["address"]
    rec = {"address": a, "label_expected": v["label"], "checksum_ok": c.to_checksum(a) == a}
    rec["has_code"] = c.get_code(a, blk) not in ("0x", "0x0", None)
    rec["name"] = c.call_string(a, "name()", blk)
    rec["symbol"] = c.call_string(a, "symbol()", blk)
    rec["decimals"] = c.call_uint(a, "decimals()", blk)
    rec["asset"] = c.call_address(a, "asset()", blk)
    rec["asset_is_usdt"] = rec["asset"].lower() == usdt
    ta = c.call_uint(a, "totalAssets()", blk)
    ts = c.call_uint(a, "totalSupply()", blk)
    rec["totalAssets_raw"] = str(ta)
    rec["totalAssets_usdt"] = str(c.fmt_units(ta, 6))
    rec["totalSupply_raw"] = str(ts)
    rec["totalSupply_shares"] = str(c.fmt_units(ts, rec["decimals"]))
    one_share = 10 ** rec["decimals"]
    pps = c.call_uint(a, "convertToAssets(uint256)", blk, c._enc_uint(one_share))
    rec["convertToAssets_1share_raw"] = str(pps)
    rec["usdt_per_share"] = str(c.fmt_units(pps, 6))
    try:
        pr = c.call_uint(a, "previewRedeem(uint256)", blk, c._enc_uint(one_share))
        rec["previewRedeem_1share_usdt"] = str(c.fmt_units(pr, 6))
    except Exception as e:  # noqa: BLE001
        rec["previewRedeem_error"] = str(e)[:200]
    try:
        sc = c.bs_get(f"/smart-contracts/{a}")
        rec["blockscout_verified_source"] = bool(sc.get("is_verified")) or bool(sc.get("source_code"))
        rec["blockscout_contract_name"] = sc.get("name")
        rec["blockscout_is_proxy"] = bool(sc.get("implementations"))
        rec["blockscout_implementations"] = sc.get("implementations")
    except Exception as e:  # noqa: BLE001
        rec["blockscout_verified_source"] = None
        rec["blockscout_sc_error"] = str(e)[:200]
    rec["verified"] = rec["has_code"] and rec["asset_is_usdt"] and rec["checksum_ok"]
    vaults[key] = rec
out["vaults"] = vaults

with open("contract_verification.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
