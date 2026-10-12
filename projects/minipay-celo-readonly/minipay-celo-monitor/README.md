# MiniPay Nur-Lese-Monitor (Celo Mainnet, Chain-ID 42220)

Dieses Werkzeug liest ausschließlich öffentliche Daten von Celo Mainnet. Es signiert nichts, sendet nichts und verbindet sich mit keiner Wallet.

## Sicherheitsdesign

| Maßnahme | Umsetzung |
|---|---|
| Nur Lesemethoden | Whitelist in `celo_readonly.py`: `eth_chainId`, `eth_blockNumber`, `eth_getBalance`, `eth_call`, `eth_getBlockByNumber`, `eth_getCode`. Jede andere Methode, z. B. `eth_sendRawTransaction`, `eth_sign`, `personal_sign` oder `wallet_*`, wird vor dem Netzwerkzugriff blockiert. |
| `eth_call` ohne Absender | Aufrufe mit `from`, `value` oder `gas` werden abgelehnt. Es handelt sich um reine Simulationen ohne Zustandsänderung. |
| Blockscout | Ausschließlich HTTP-GET (API v2 sowie v1 `getLogs` für nach Topics gefilterte Vault-Ereignisse), gedrosselt auf ca. 3 Anfragen/s. |
| Keine Geheimnisse | Es gibt keine Eingabe für Passwörter, Schlüssel, Seed-/Wiederherstellungsphrasen, SMS- oder 2FA-Codes und keine Signaturbibliothek. |
| Bestätigungspflicht | `report` startet nur mit `--confirmed`, also nachdem der Nutzer die gekürzt angezeigte Adresse bestätigt hat. |
| Zuordnung nur mit Zustimmung | `bind` schreibt die Zuordnung Adresse ↔ Account nur mit `--consent`. Gespeichert werden ausschließlich die öffentliche Adresse und ein Hinweis zum Umfang („nur lesen“). |
| Prüfprotokoll | Jeder Bericht listet am Ende alle Netzwerkzugriffe nach Methode auf. |

## Befehle

```bash
python3 minipay_report.py validate 0x…                      # Formatprüfung, offline
python3 minipay_report.py report   0x… --confirmed [--days N] --out reports
python3 minipay_report.py bind     0x… --consent --account-label <E-Mail>
python3 verify_contracts.py                                  # Token-/Vault-Verträge prüfen (ohne Wallet)
```

## Geprüfte Verträge (on-chain verifiziert am 2026-10-02, Block 79 037 788)

| Asset | Vertrag | On-Chain-Symbol | Dezimalstellen |
|---|---|---|---:|
| USDT | `0x48065fbBE25f71C9282ddf5e1cD6D6A887483D5e` | USD₮ | 6 |
| USDC | `0xcebA9300f2b948710d2653dD7B07f33A8B32118C` | USDC | 6 |
| USDm (früher cUSD) | `0x765DE816845861e75A25fCA122bb6898B8B1282a` | USDm | 18 |
| EURm (früher cEUR) | `0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73` | EURm | 18 |
| MiniPay Aave V3 USDT (ERC-4626) | `0xbaD4711D689329E315Be3E7C1C64CF652868C56c` | mpAaveUSDT, asset() = USDT | 6 |
| MiniPay Morpho Feather USDT (ERC-4626) | `0x440933053Fb430cABf8152F59F5967cE0FeB5f15` | mpFeatherUSDT, asset() = USDT | 6 |

## Ausgaben je Bericht

- `minipay_bericht_<Zeit>.md`: der Bericht (Bestände, Earn, Eingänge, Boost, Methodik, Risiken, Datenschutz, Nur-Lese-Nachweis)
- `minipay_transfers_<Zeit>.csv`: alle Token-Transfers mit Kategorie, Sicherheit der Zuordnung, Begründung und Explorer-Link
- `minipay_daten_<Zeit>.json`: Rohdaten zur Nachprüfung

## Grenzen

- Für MiniPay Boost ist kein offizieller Auszahler öffentlich dokumentiert. Boost-Zuordnungen bleiben Annahmen („nicht abschließend zuordenbar“).
- Erfasst werden nur die beiden konfigurierten Earn-Vaults.
- Blockscout begrenzt die Anfragen auf etwa 10 pro Zeitfenster. Bei sehr großen Historien kann ein Lauf deshalb einige Minuten dauern.
