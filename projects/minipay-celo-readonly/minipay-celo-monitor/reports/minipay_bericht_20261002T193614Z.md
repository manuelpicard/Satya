# MiniPay-Wallet: Nur-Lese-Bericht (Celo Mainnet)

| Feld | Wert |
|---|---|
| Abfragezeitpunkt (UTC) | 2026-10-02 19:36:14 UTC |
| Netzwerk | Celo Mainnet |
| Chain-ID (on-chain geprüft) | 42220 |
| Bestätigte Wallet-Adresse (gekürzt) | `0x107B…78B4` |
| Referenzblock | [79069018](https://celo.blockscout.com/block/79069018) (2026-10-02 19:36:16 UTC) |
| Betrachteter Zeitraum der Historie | gesamter von Blockscout verfügbarer Verlauf |
| Modus | Nur lesend: keine Signatur, keine Transaktion, keine Wallet-Verbindung |

> **Kennzeichnung:** Alle Beträge sind **On-Chain-Beobachtungen** auf Celo Mainnet. Ein Eintrag auf der Blockchain allein beweist nicht, dass er von MiniPay, Opera oder einem bestimmten Programm stammt.

## 1. Bestände zum Referenzblock

### 1.1 Nativer CELO-Bestand

| Asset | Bestand | Rohwert (wei) | Dezimalstellen | Methode | Block |
|---|---:|---:|---:|---|---:|
| CELO | 0.000000 | 0 | 18 | eth_getBalance | 79069018 |

### 1.2 Verifizierte Stablecoin-Bestände

| Asset | On-Chain-Symbol | Vertrag | Dezimalstellen (on-chain/erwartet) | Metadaten verifiziert | Bestand | Rohwert |
|---|---|---|---|---|---:|---:|
| USDT | USD₮ | [0x4806…3D5e](https://celo.blockscout.com/address/0x48065fbBE25f71C9282ddf5e1cD6D6A887483D5e) | 6/6 | ja | 12.818252 | 12818252 |
| USDC | USDC | [0xcebA…118C](https://celo.blockscout.com/address/0xcebA9300f2b948710d2653dD7B07f33A8B32118C) | 6/6 | ja | 0.000000 | 0 |
| USDm | USDm | [0x765D…282a](https://celo.blockscout.com/address/0x765DE816845861e75A25fCA122bb6898B8B1282a) | 18/18 | ja | 0.000000 | 0 |
| EURm | EURm | [0xD876…cA73](https://celo.blockscout.com/address/0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73) | 18/18 | ja | 0.000000 | 0 |

**Summe verifizierter USD-Stablecoins (USDT + USDC + USDm, nominal 1:1, ohne Kursumrechnung):** 12.818252. EURm wird getrennt geführt (0.000000 EURm) und nicht in USD umgerechnet. Vault-Positionen sind in dieser Summe nicht enthalten (siehe Abschnitt 2).

### 1.3 Weitere Token (unverifiziert, nicht in Summen)

Keine weiteren Token laut Blockscout.

## 2. MiniPay Earn: geschätzte Vault-Positionen

> MiniPay Earn ist ein **separates DeFi-Angebot** (Drittanbieter-Strategien über ERC-4626-Vaults) und nicht dasselbe wie die tägliche Boost-Ausschüttung. Vertrags- oder Tokennamen sind keine Sicherheitsgarantie.

| Vault | Vertrag | Basisanlage (asset()) | Gehaltene Shares | Gegenwert convertToAssets (USDT) | previewRedeem (USDT) | maxWithdraw (USDT) | Block |
|---|---|---|---:|---:|---:|---:|---:|
| mpAaveUSDT (MiniPay Aave V3 USDT) | [0xbaD4…C56c](https://celo.blockscout.com/address/0xbaD4711D689329E315Be3E7C1C64CF652868C56c) | USDT (verifiziert) | 0.000000 | 0.000000 | – | – | 79069018 |
| mpFeatherUSDT (MiniPay Morpho Feather USDT) | [0x4409…5f15](https://celo.blockscout.com/address/0x440933053Fb430cABf8152F59F5967cE0FeB5f15) | USDT (verifiziert) | 0.000000 | 0.000000 | – | – | 79069018 |

**Keine erkennbare Position in den geprüften MiniPay-Earn-Vaults** zum Referenzblock.

Abfragezeitpunkt der Vault-Werte: 2026-10-02 19:36:16 UTC, Block 79069018. Der geschätzte Gegenwert kann sich bis zu einer tatsächlichen Rückgabe ändern (Zinsentwicklung, Gebühren, Liquidität der zugrunde liegenden Protokolle).

### 2.1 Erkannte Einzahlungen und Auszahlungen (Deposit-/Withdraw-Ereignisse)

Keine Deposit-, Withdraw-, Mint- oder Redeem-Ereignisse dieser Adresse in den geprüften Vaults gefunden (Mint/Redeem erzeugen nach ERC-4626 ebenfalls Deposit-/Withdraw-Ereignisse).

## 3. Eingehende Werte: Transaktionsübersicht

Quelle: Celo-Blockscout-API v2 (`/addresses/…/token-transfers`, `/transactions`, `/internal-transactions`), Seiten abgerufen: 1, vollständig im Zeitraum: ja.

### 3.1 Bestätigte USDT-Eingänge nach Kategorie (verifizierter USDT-Vertrag)

| Kategorie | Anzahl | Summe USDT |
|---|---:|---:|
| On-Ramp / Bridge / Dienstleister (möglich) | 1 | 12.818252 |

„Bestätigt“ bedeutet hier nur: Der Transfer stammt vom verifizierten USDT-Vertrag und ist on-chain eingetragen. Die Herkunft (Kategorie) ist davon getrennt zu bewerten.

### 3.2 Einzelaufstellung eingehender Token-Transfers

| Datum/Uhrzeit (UTC) | Betrag | Asset | Absender | Kategorie | Sicherheit der Zuordnung | Begründung | Explorer |
|---|---:|---|---|---|---|---|---|
| 2026-10-02 12:38:45 UTC | 12.818252 | USDT | [0xc9b2…a2b6](https://celo.blockscout.com/address/0xc9b29db51142b00E697385092b80efc57402a2b6) | On-Ramp / Bridge / Dienstleister (möglich) | niedrig | Absender ist ein Smart Contract; Blockscout-Name „DaimoPayExecutor“ (Drittangabe); Absender mit sehr vielen Transfers (90973), aber ohne Boost-Muster. | [0xfc1f2276…](https://celo.blockscout.com/tx/0xfc1f2276dd4b060096a361c588140058f6c3e510e8388f0344789ecc5b7e72df) |

### 3.3 Eingehende native CELO-Beträge

Keine eingehenden nativen CELO-Beträge im Zeitraum.

## 4. Mögliche MiniPay-Boost-Erträge (Annahme)

| Zeitraum (bis Referenzblock) | Anzahl | Summe USDT | Erster | Letzter |
|---|---:|---:|---|---|
| 24 Stunden | 0 | 0.000000 | – | – |
| 7 Tage | 0 | 0.000000 | – | – |
| 30 Tage | 0 | 0.000000 | – | – |
| Gesamt (abgefragter Verlauf) | 0 | 0.000000 | – | – |

> **Annahme-Kennzeichnung:** Für MiniPay Boost ist kein offizieller Auszahler on-chain verifiziert oder öffentlich dokumentiert. Alle hier zusammengefassten Beträge sind deshalb „möglicher MiniPay-Boost-Ertrag – nicht abschließend zuordenbar“. Derselbe Absender kann auch andere MiniPay-Aktionen auszahlen, z. B. Kampagnen, Empfehlungs- oder Aufgabenprämien.

Einordnung: Nach den [Boost-Bedingungen](https://minipay.to/minipay-boost-terms-conditions) beträgt die Belohnung **bis zu** 2 % pro Woche auf USDT, höchstens 10 USDT pro Woche (außer bei Kampagnen), bei mindestens 1 USDT Bestand. Sie wird wöchentlich berechnet und täglich ausgeschüttet. Das ist **kein garantierter Satz**: Stufen, Nutzung und Programmänderungen beeinflussen den tatsächlichen Betrag. Ein Vergleich der beobachteten Summen mit dem Maximum ist deshalb kein Anspruchsnachweis.

## 5. Methodik, Datenlücken und Annahmen

**Klassifikationsregeln (für jede Zeile ist die Begründung angegeben):**

- *Möglicher MiniPay-Boost-Ertrag – nicht abschließend zuordenbar*: USDT-Eingänge eines Absenders mit mindestens 3 Eingängen an mindestens 3 Tagen, mindestens 60 % der Abstände im ~24-h-Raster (±4 h), Einzelbeträge ≤ 10 USDT, keine Ausgänge der Wallet an diesen Absender, Absender mit ≥ 10,000 Token-Transfers (Massenauszahler).
- *Vault-Einzahlung (MiniPay Earn)* / *Vault-Auszahlung (MiniPay Earn)*: USDT-Bewegung in einer Transaktion mit ERC-4626-Deposit- bzw. Withdraw-Event der geprüften Vaults für diese Adresse.
- *Rückzahlung / Erstattung (möglich)*: Betrag entspricht (±1 %) einem früheren Ausgang an denselben Absender innerhalb von 30 Tagen.
- *On-Ramp / Bridge / Dienstleister (möglich)*: Absender ist ein Smart Contract, hat einen Blockscout-Namen oder -Tag (Drittangabe) oder ist ein Massenabsender ohne Boost-Muster.
- *P2P-Eingang (wahrscheinlich)*: Absender ist eine gewöhnliche Adresse mit geringem Transfervolumen oder hat zuvor Zahlungen von dieser Wallet erhalten.
- *Unbekannter Eingang*: keine belastbaren Merkmale. *Unverifizierter Token – nicht in Summen*: Token außerhalb der verifizierten Verträge.

**Datenlücken, Fehler und Hinweise:**

- Vault-Ereignisse mpFeatherUSDT: möglicherweise unvollständig. Quelle: Fallback: /transactions/{hash}/logs (nur abgefragter Zeitraum). Hinweise: Primärquelle getLogs fehlgeschlagen (share_in: Blockscout v1 GET fehlgeschlagen: HTTP 429 (Rate-Limit)); Ausweichroute verwendet
- Für MiniPay Boost ist kein offizieller Auszahler on-chain verifiziert oder öffentlich dokumentiert; Boost-Zuordnungen sind Annahmen.
- Historische Bestände zu früheren Blöcken wurden nicht rekonstruiert. Eine effektive Boost-Rendite pro Woche wird deshalb nicht berechnet.
- Gasgebühren, die MiniPay in Stablecoins zahlt (Celo Fee Abstraction), erscheinen nicht zwingend als Token-Transfer. Der Bericht rekonstruiert keine Salden aus Transfers.
- Blockscout-Namen und -Tags sind Drittangaben und gelten nicht als offizielle Verifizierung.
- Weitere, hier nicht konfigurierte Earn-Vaults oder Strategien werden nicht erfasst. Geprüft wurden nur mpAaveUSDT und mpFeatherUSDT.
- Transfers nach dem Referenzblock bleiben unberücksichtigt, damit Bestände und Historie konsistent sind.

## 6. Risiken

- **MiniPay Earn** umfasst Drittanbieter- und DeFi-Risiken, etwa Smart-Contract-, Protokoll-, Liquiditäts-, Oracle- und Stablecoin-Risiken (Aave V3, Morpho/Feather, Vault-Betreiber). Vergangene Renditen sind keine Zusage. Der Gegenwert ist eine Schätzung zum Referenzblock.
- **MiniPay Boost** ist ein freiwilliges Prämienprogramm, das jederzeit geändert, ausgesetzt oder beendet werden kann.
- **Unverifizierte Token** können Betrugsversuche sein (z. B. gefälschte USDT-Kopien). Nicht damit interagieren.
- **Stablecoins** können ihre Bindung verlieren. Hier wird nominal 1:1 und ohne Kursbewertung gerechnet.

## 7. Datenschutz

Alle Celo-Mainnet-Daten dieser Adresse sind öffentlich einsehbar: Bestände, Transfers und Gegenparteien. Die Zuordnung der Adresse zu einer Person oder einem Manus-Account ist **datenschutzrelevant**, denn wer die Zuordnung kennt, kann die gesamte Finanzhistorie dieser Adresse verfolgen. Dieser Bericht enthält Explorer-Links, aus denen die vollständige Adresse ableitbar ist. Bitte nur bewusst teilen.

## 8. Nachweis des Nur-Lese-Betriebs

| Zugriff | Anzahl |
|---|---:|
| RPC `eth_blockNumber` (forno.celo.org) | 1 |
| RPC `eth_call` (forno.celo.org) | 24 |
| RPC `eth_chainId` (forno.celo.org) | 1 |
| RPC `eth_getBalance` (forno.celo.org) | 1 |
| RPC `eth_getBlockByNumber` (forno.celo.org) | 1 |
| RPC `eth_getCode` (forno.celo.org) | 1 |
| HTTP GET blockscout_api_v1_getLogs | 11 |
| HTTP GET blockscout_api_v2 | 7 |

Es wurden keine Signaturen angefordert, keine Transaktionen erzeugt oder gesendet und keine Wallet-Verbindung hergestellt. Geheime Daten (Passwörter, private Schlüssel, Seed- oder Wiederherstellungsphrasen, SMS- oder 2FA-Codes) wurden weder angefordert noch verarbeitet. Jede künftige Aktion mit echten Vermögenswerten ist ein neuer, schreibender Vorgang. Er wird vorher mit Betrag, Ziel, Gebühren, Risiken und Konsequenzen beschrieben und muss von Ihnen ausdrücklich freigegeben und in Ihrer eigenen Wallet bestätigt werden.
