# Gesprächs- und Projektübergabe: MiniPay Celo Nur-Lese-Monitor

> **Vertraulich — nur für das private Repository.** Diese Notiz enthält E-Mail-Adresse, vollständige öffentliche Wallet-Adresse, Bestände und Transaktionsverknüpfungen. Sie darf nicht in öffentliche Repositories kopiert oder weitergegeben werden. Das Repository ist bei GitHub als privat angelegt; Eigentümer und alle hinzugefügten Collaborators können Inhalte trotzdem sehen.

## 1. Nutzerauftrag im Kern

Der Nutzer möchte eingehende Celo-/MiniPay-Werte transparent und sicher über seinen Manus-Account verwalten. Seine ausdrückliche Ausgangsanforderung liegt vollständig und unverändert in [`original-request.txt`](original-request.txt).

Kernanforderungen:

- Nur-Lese-Überwachung von **MiniPay / Celo Mainnet**, Chain-ID `42220`.
- Bestände: CELO, USDT, USDC, USDm (früher cUSD), EURm (früher cEUR); Vertragsmetadaten on-chain prüfen.
- Erkennen und dokumentieren eingehender Transfers, mögliche MiniPay Boost-Erträge und zwei MiniPay Earn ERC-4626-Vaults.
- Keine Passwörter, Schlüssel, Seed-/Recovery-Phrasen, SMS-/2FA-Codes anfragen oder speichern.
- Keine Signatur, Transaktion, Auszahlung, Anlage, Tausch, Opera-/MiniPay-Einstellungsänderung oder sonstige Vermögensverfügung.
- On-chain-Beobachtung nicht mit Herkunfts- oder MiniPay-Nachweis gleichsetzen.
- Unverifizierte Token separat führen, nicht in Summen einrechnen.
- Jede künftige schreibende Aktion braucht einen neuen Auftrag, eine genaue Beschreibung von Betrag/Ziel/Gebühren/Risiken/Folgen und Bestätigung in der eigenen Wallet.
- Benachrichtigungen nur nach separater Wahl von Kanal und Auslöser; bisher keine Routine eingerichtet.

## 2. Identität und bewilligte Wallet

- Manus-Account-E-Mail, die der Nutzer im Auftrag nannte: `manuel.picard@web.de`.
- Vom Nutzer am 2026-10-03 angegebene öffentliche Celo-Adresse: `0x107B8eA19996De0CC43A28A7F8ec9a0E529778B4`.
- Offline-Formatprüfung: 42 Zeichen; EIP-55-Prüfsumme korrekt; verkürzt `0x107B…78B4`.
- Nutzer sagte: „es ist die Opera minipay Adresse“. Die Adresse wurde daraufhin als bestätigt verwendet.
- Die Zuordnung der Adresse zu E-Mail/Manus-Account wurde **nicht dauerhaft gespeichert**. Keine `wallet_binding.json` erzeugt. Für das explizite Speichern der Zuordnung ist weiterhin eine separate klare Zustimmung einzuholen.
- Nutzer erwähnte „celo wird hier verbrannt“. Erklärung: Die Überwachung selbst führt keine Transaktion aus und belastet/verbrennt kein CELO aus der Wallet. Der beobachtete native CELO-Saldo war bei den letzten Messungen null.

## 3. Gesprächsverlauf und Entscheidungen

### 2026-10-02 — ursprüngliche Spezifikation

Der Nutzer lieferte eine ausführliche Anforderung (vollständig archiviert in `original-request.txt`) mit einer Voraussetzung: Adresse zunächst syntaktisch prüfen, gekürzt anzeigen und erst nach Nutzerbestätigung abfragen. Er erlaubte nur die öffentliche Adresse, keine Zugangsdaten. Benachrichtigungen blieben auf manuelle Abfragen beschränkt, bis eine Routine gewählt wird.

Vor Wallet-Eingabe wurden nur Chain-ID/Blockhöhe und Contract-Metadaten der festen Token-/Vault-Verträge gelesen. Ergebnisse: Forno meldete Chain-ID `42220` (`0xa4ec`). On-chain-Symbole/Dezimalstellen stimmten mit der Spezifikation überein. Die beiden Vaults hatten `asset()` gleich USDT.

MiniPay Boost Terms wurden abgerufen: bis zu 2 % pro Woche auf qualifizierendes USDT-Guthaben, bis 10 USDT/Woche außer Sonderaktionen, Auszahlung täglich; Bedingungen und Beträge können sich ändern und sind nicht garantiert. MiniPay Earn ist davon getrennt.

### 2026-10-02 / 2026-10-03 — zunächst fehlende Adresse, danach Bestätigung

Eine Nachricht enthielt nur den Platzhalter `[Deine Adresse einfügen]`. Die lokale Syntaxprüfung war ungültig; zu diesem Zeitpunkt wurde **keine** Wallet abgefragt.

Der Nutzer reichte danach die vollständige Adresse aus Abschnitt 2 ein. Sie wurde zunächst offline geprüft und gekürzt gezeigt. Der Nutzer bestätigte: „es ist die Opera minipay Adresse“. Erst danach startete die On-chain-Leseabfrage.

### 2026-10-03 — erster Nur-Lese-Bericht

Abfragezeit UTC: `2026-10-02 19:36:14`, Referenzblock `79 069 018`.

- Chain-ID `42220`.
- CELO `0`.
- USDT `12.818252`; USDC/USDm/EURm `0`.
- Keine erkennbaren Shares in `mpAaveUSDT` oder `mpFeatherUSDT`.
- Ein verifizierter USDT-Eingang von `12.818252`, Blockscout-benannter Smart Contract „DaimoPayExecutor“, als mögliche On-Ramp-/Bridge-/Dienstleister-Bewegung (niedrige Zuordnungssicherheit), nicht als MiniPay-Beweis.
- Keine als möglicher Boost klassifizierten Eingänge.
- Eine vollständige `mpFeatherUSDT`-Ereignisabfrage war wegen Blockscout HTTP 429 eingeschränkt.

### 2026-10-07 — aktualisierter Nur-Lese-Bericht

Abfragezeit UTC: `2026-10-07 00:53:30`, Referenzblock `79 433 654`.

- CELO `0`.
- USDT `12.860923`; USDC `0`; USDm `0`; EURm `0`.
- Keine aktuellen Shares in den beiden geprüften MiniPay-Earn-Vaults.
- Insgesamt 5 USDT-Eingänge laut Blockscout-Historie (eine API-Seite, im verfügbaren Verlauf vollständig):
  1. `12.818252 USDT`, am `2026-10-02 12:38:45 UTC`, vom Contract `0xc9b29db51142b00E697385092b80efc57402a2b6`; Blockscout-Name „DaimoPayExecutor“; mögliche On-Ramp/Bridge/Dienstleister-Zuordnung, niedrig.
  2. `0.010952 USDT`, `2026-10-03 05:16:46 UTC`, Sender `0x5CDF62f29478C4B215a3Ba21059A2B3cb7d44b62`.
  3. `0.010966 USDT`, `2026-10-04 05:22:46 UTC`, gleicher Sender.
  4. `0.010980 USDT`, `2026-10-05 05:18:59 UTC`, gleicher Sender.
  5. `0.009773 USDT`, `2026-10-06 05:42:44 UTC`, gleicher Sender.
- Transfers 2–5 ergeben zusammen `0.042671 USDT`. Ihr ~24-h-Muster und der als Smart Contract erkannte Massensender passen zu möglichem Boost. **Nicht offiziell verifiziert**; kategorisiert als „Möglicher MiniPay-Boost-Ertrag — nicht abschließend zuordenbar“. Kein Beweis für Boost; andere Prämien-/Programmzahlungen sind möglich.
- Boost-Zeitfenster zum damaligen Referenzblock: 24 h = `0.009773`; 7 Tage = `0.042671`; 30 Tage = `0.042671`; gesamte verfügbare Historie = `0.042671`.
- Keine eingehenden nativen CELO-Transfers im verfügbaren Verlauf.
- Blockscout lieferte für `mpFeatherUSDT` erneut HTTP 429 bei der umfassenden Logabfrage; Ausweichroute war zeitlich begrenzt. Der On-chain-Share-Saldo ist null, aber historische Ereignisvollständigkeit blieb eingeschränkt.

## 4. Berichte und Nachvollziehbarkeit

Beide Momentaufnahmen liegen in [`../reports/`](../reports/):

- `minipay_bericht_20261002T193614Z.md`, `minipay_transfers_20261002T193614Z.csv`, `minipay_daten_20261002T193614Z.json`
- `minipay_bericht_20261007T005330Z.md`, `minipay_transfers_20261007T005330Z.csv`, `minipay_daten_20261007T005330Z.json`

Die CSVs enthalten Explorer-Links mit vollständigen Transaktions-Hashes. Der JSON-Rohdatensatz hält Zeitstempel, Blocks, Verträge, Absender, Rohbeträge und Klassifikationsbegründungen fest.

## 5. Read-only Implementierung

Im Ordner `../` liegen `celo_readonly.py`, `minipay_report.py`, `verify_contracts.py`, `contract_verification.json` und `README.md`.

Die RPC-Whitelist erlaubt ausschließlich `eth_chainId`, `eth_blockNumber`, `eth_getBalance`, `eth_call`, `eth_getBlockByNumber` und `eth_getCode`. Schreib-/Signiermethoden wie `eth_sendTransaction`, `eth_sendRawTransaction`, `eth_sign`, `personal_sign`, `eth_signTypedData*` und `wallet_*` werden vor Netzwerkzugriff abgelehnt. `eth_call` ist ohne `from`/`value`/`gas`. Blockscout-Zugriffe sind GET-only.

Abfragen erfolgten über `https://forno.celo.org` und `https://celo.blockscout.com/api/v2` (gefilterte Logs über Blockscout `getLogs`). Abschlussberichte enthalten ein Audit der verwendeten Methoden. Es wurden keine Geheimnisse verarbeitet und keine Transaktionen gesendet.

## 6. GitHub-Entscheidung (2026-10-08 bis 2026-10-12)

- Der Nutzer bat um einen passenden GitHub-Ordner.
- Er genehmigte zunächst einen generischen Ordner ohne Wallet-Daten in `makopipokam/manualai.org`.
- Danach bat er darum, den gesamten Gesprächsinhalt hochzuladen und bestätigte ausdrücklich den Upload sensibler Informationen in dem öffentlichen Repository.
- Anschließend änderte er seine Präferenz: „doch lieber privat“.
- Ergebnis: ein dediziertes privates Repo `https://github.com/makopipokam/minipay-celo-readonly`; **kein Inhalt wurde in `manualai.org` veröffentlicht**.
- Dieser Kontext, der Originalauftrag, generischer Code und beide Berichtstände sind für die spätere Nutzung in `minipay-celo-monitor/` zusammengeführt.

## 7. Noch offene Aufgaben / sicher weiterarbeiten

1. Der jüngste Messpunkt ist `2026-10-07 00:53 UTC`, nicht live. Bei aktuellem Status zuerst erneut einen Nur-Lese-Bericht erzeugen und klar zeitstempeln.
2. `mpFeatherUSDT`-Historie blieb teils API-rate-limitiert. Für eine sichere Aussage über frühere Ein-/Auszahlungen eine robuste, gedrosselte Pagination bzw. alternative verlässliche Logs-Quelle verwenden; Lücken weiter sichtbar kennzeichnen.
3. Nutzer fragen, ob manuelle Abfragen genügen oder ein rein informatives Benachrichtigungsschema gewünscht ist. Vor Benachrichtigungen Kanal und Trigger erheben. Nie automatisch Finanzentscheidungen auslösen.
4. Wenn Wallet-Adresse ↔ `manuel.picard@web.de` dauerhaft gespeichert werden soll: vorher separate ausdrückliche Zustimmung einholen. Der bisherige GitHub-Upload ist **kein** Zustimmungseintrag in Manus-Account-Konfiguration.
5. Keine Transaktionen, Signaturen, Smart-Contract-Schreibaufrufe, Wallet-Verbindungen mit Schreibrechten oder Einstellungen in Opera/MiniPay. Eine öffentliche Adresse allein ist nie Ausgabeberechtigung.

## Quellen

- [Celo Forno RPC](https://forno.celo.org)
- [Celo Blockscout API v2](https://celo.blockscout.com/api/v2)
- [MiniPay Boost Terms & Conditions](https://minipay.to/minipay-boost-terms-conditions)
- [Kiln / MiniPay Earn-Ankündigung](https://www.kiln.fi/post/kiln-powers-stablecoin-earn-product-for-minipay-users-on-celo-targeting-1-3b-unbanked-globally)
