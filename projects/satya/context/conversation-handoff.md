# Satya — Projekt- und Konversationskontext für zukünftige KI-Sitzungen

**Stand:** 14. Oktober 2026
**Zweck:** Dauerhafte, weiterverwendbare Übergabe zu Satya: Nutzerziele, Entscheidungen, Architektur, verifizierter Projektstand, Grenzen und nächste Schritte.

> **Archivhinweis:** Dies ist eine kuratierte Projekterinnerung aus dem in der aktuellen Sitzung verfügbaren Verlauf. Frühere Gesprächsteile wurden beim Sitzungswechsel zusammengefasst; daher ist dies kein wortgetreues Volltranskript aller historischen Assistentenantworten. Verfügbare ursprüngliche Nutzerformulierungen sind unten erhalten. Interne System-/Entwicklerinstruktionen, Zugangsdaten, persönliche Wallet-Schlüssel und private Tooldaten gehören nicht in dieses private Archiv.

## Projektziel und feste Produktgrenzen

Satya ist ein Celo-basiertes System zur nachvollziehbaren Herkunftserklärung von digitalen Inhalten. Es bindet prüfbare, signierte Aussagen an einen Content-Hash und kann pro Anfrage einen bezahlten Prüfservice über x402 anbieten. Der Schwerpunkt ist **Provenienz und Rechenschaft**, nicht ein universeller KI-Detektor.

Ein Ergebnis darf nur dann als **gewiss** dargestellt werden, wenn ein passender kryptografischer Beweis geprüft wurde. Ohne passende, gültige Evidenz lautet es **unbestimmt**. Fehlende KI-Metadaten, C2PA-Angaben oder Registry-Einträge beweisen keine menschliche Urheberschaft. Ein Self-Proof belegt ein Proof-of-Personhood-Kriterium, beweist für sich allein aber nicht, dass die Person einen bestimmten Inhalt erstellt hat. Eine signierte Aussage belegt, wer sie abgegeben hat — nicht, dass sie wahr ist.

Keine Oberfläche oder Dokumentation darf versprechen, Satya könne zweifelsfrei feststellen, ob beliebiger Inhalt durch irgendeine KI entstanden ist.

## Nutzerentscheidungen und erhaltener Gesprächsverlauf

Die folgenden Formulierungen stammen aus den erhaltenen Nutzerbeiträgen. Die historische Reihenfolge ist erhalten; für frühere Beiträge sind nicht durchgängig Zeitstempel verfügbar.

1. „ich will einen cryptotoken entwickeln dessen einziger Zweck ist KI von nicht KI zu unterscheiden und nicht KI zu authentifizieren“
2. „entwickle Satyagiri, sodass er todsicher sagen kann ob ein Inhalt durch irgendeine KI generiert wurde“
3. „nutze den hackerton um diesen Plan umzusetzen“
4. „celo“
5. „celo“
6. „das Projekt heißt jetzt nur ich satya. ohne giri“
7. „nutze den hackerton um Celo zu generieren“
8. „noch was?“
9. „noch was?“
10. „mach das“
11. „Bitte fortfahren.“
12. „Erstelle eine Übersicht der nächsten Schritte zur Finalisierung des Projekts 'Satya'.“
13. „dann mach ihn soulbound“
14. „1 – Soulbound-Menschennachweis“
15. „erstelle dazu einen passenden GitHub ordner“
16. Am 12. Oktober 2026: „Now continue the task based on the inherited context and files. Re-read all relevant skills to the current task before proceeding.“
17. Am 12. Oktober 2026: „Bitte fortfahren.“
18. Am 14. Oktober 2026: „lade den gesamten Inhalt dieser Konversation in einen relevanten Ordner auf GitHub hoch, sodass sie von einer zukünftigen KI wieder benutzt werden kann.“
19. Am 14. Oktober 2026: „in die Satya repo von manuelpicard“ — gemeint ist das private Repository `manuelpicard/Satya`.

Weitergeltende Wünsche: Name **Satya** (nicht Satyagiri); Celo; Soulbound-Menschennachweis; Hackathon-Nutzung zur Umsetzung/Sichtbarkeit; sichere Urteile nur bei kryptografischem Beleg, andernfalls **unbestimmt**; Kommunikation auf Deutsch.

## Architektur und Status

- **Identität:** Self Agent ID / Self-Proof-of-Personhood; frischer Proof und Agent-ID-Wallet-Eigentum werden geprüft.
- **Aktuelle Celo-Provenienz:** `SatyaCelo` unterstützt Self-Human-, Self-Agent- und ERC-8004-Agent-Aussagen. Es ist ownerless und erlaubt, Selbstwidersprüchlichkeit nachzuweisen. ERC-8004-Agenten können nur `AI_GENERATED` erklären, keine menschliche Urheberschaft.
- **Legacy-Registry:** `SatyaRegistry` ist ein separates HMN-/`HumanCredential`-basiertes Register mit Provider-/Fraud-Governance und Eigentümerrechten. Nicht mit dem ownerless `SatyaCelo` verwechseln.
- **Soulbound Credential:** `contracts/src/credentials/SatyaHumanSBT.sol` implementiert ERC-5192. Claim/Refresh erfordert einen frischen Self-Proof; Recovery verlangt dieselbe verifizierte Person; Renounce verbrennt das Credential. Transfers/Freigaben sind gesperrt. Das Credential beweist keine Inhaltsautorenschaft. Es ist noch nicht deployed und hat keine Mint-/Recovery-UI.
- **Frontend:** Next.js 15 / React 19 / Viem. Dateien (bis 50 MB) werden im Browser gehasht; Text wird als `satya-text-v1` normalisiert. Wallet-/Transaktionsfreigaben bleiben beim Nutzer.
- **Python-Engine:** Separater FastAPI-/Uvicorn-Baum mit C2PA-Trust-Listen, Hashing, Metadaten-/Wasserzeichenhinweisen, EIP-712-Siegeln, Registerabfragen und deterministischer Urteilslogik. Optionaler x402-Endpunkt.
- **x402:** Historische Entwicklung dokumentiert erfolgreiche Testnet-USDC-Abwicklung. Beim letzten lokalen Statuscheck war Port 8000 frei; ein temporärer Start meldete `celo: null`, `x402: null` (keine Runtime-Konfiguration). In der letzten Implementierungsrunde wurden keine Zahlung, Signatur oder Transaktion ausgelöst.
- Die vollständige Modul-/Dateiinventur samt Rollen, Quellbaumgrenzen, Testabdeckung und Sicherheitsnotizen steht in [`module-inventory.md`](module-inventory.md).

### Wichtige Nullifier-/Datenschutzkorrektur (Audit 14. Oktober)

Eine frühere Handoff-Fassung behauptete fälschlich, kein Contract-API/Event exponiere den Nullifier. **Das trifft nicht auf `SatyaCelo` zu:** Event `Declared` enthält den vollen Nullifier; `attestation(s)` und `humanBehind()` geben ihn ebenfalls zurück. `celo_ledger.py` kürzt ihn nur in der JSON-Antwort; auf der öffentlichen Chain bleibt er vollständig lesbar. `SatyaRegistry` veröffentlicht eine HMN-`personId`. `SatyaHumanSBT` exponiert den Nullifier nicht über ein dediziertes Getter/Event, aber EVM-Storage ist grundsätzlich öffentlich lesbar. Es gibt daher keine Anonymitätsgarantie; vor Mainnet ist eine gezielte Datenschutz-/Linkability-Prüfung erforderlich.

## Testnet-Adressen und Deployments

- Celo Sepolia Chain ID: `11142220`
- `SatyaCelo`: `0x58d5f2c2ac866D7828b7e2Bf1A3542C3536c3001` (im früheren Projektstand auf Blockscout als verifiziert dokumentiert)
- Self Agent ID Registry: `0x043DaCac8b0771DD5b444bCC88f2f8BBDBEdd379`
- ERC-8004 Sepolia Registry: `0x8004A818BFB912233c491871b3d84c89A494BD9e`; Satya-Agent-ID laut Projekt-README: `453`
- x402-Test-USDC: `0x01C5C0122039549AD1493B8220cABEdD739BC44E`

Alle oben genannten Netz-/Tokenwerte beziehen sich auf Sepolia/Testnet. Test-Token haben keinen Mainnet-Wert. `SatyaHumanSBT` hat keine Deployment-Adresse; es gab kein Mainnet-Deployment.

## Quellcode, Tests und Demos

- `satya-agent/` ist die separate lokale Git-Arbeitskopie mit Next.js-App, `contracts/` und Docs. Lokaler Commit: `46fdf39` (`Add soulbound human credential and hackathon readiness`); dort war kein GitHub-Remote konfiguriert.
- Das Python-Paket `satya/` und seine Tests sind ein separater lokaler Projektbaum ohne Git-Repository. Die Engine und der Contract-/App-Quellcode wurden **nicht** in dieses private GitHub-Kontextarchiv kopiert; `manuelpicard/Satya` enthält hier nur Dokumentation.
- Solidity-Abhängigkeiten sind per Git-Submodule gepinnt: OpenZeppelin `v5.7.0`, `forge-std` `v1.17.0`; nach Clone `git submodule update --init --recursive`.
- Nach `forge clean` bestanden **60/60 Foundry-Tests** (29 `SatyaCelo`, 17 `SatyaRegistry`, 14 SBT) und **20/20 Python-Tests**. Auch das Übergabe-ZIP wurde entpackt und die Contract-/Python-Tests darin erfolgreich ausgeführt. TypeScript-Prüfung und Next.js-Produktionsbuild waren im vorherigen Projektstand erfolgreich.
- Das Demo-Korpus enthält 22 Fälle. Die dokumentierte interne Stichprobe ergab 9 sichere Urteile, davon eines falsch; im kleinen Korpus wurden keine menschlichen Inhalte fälschlich als KI eingeordnet. Dies ist kein generalisierbarer Genauigkeitsnachweis.
- Es gibt lokale Demo-CA-/Anvil-Schlüsselmaterialien und den `/api/demo/siegeln`-Pfad. Diese sind nur für Demonstration/Tests bestimmt; Schlüsselwerte gehören nicht ins Archiv und dürfen nie produktiv verwendet werden.

## Hackathon: Agents on Open Rails

Offizielle Eventseite: <https://www.loops.house/agents-on-open-rails> (zuletzt geprüft am 12. Oktober 2026).

- Anmelde- und Einreichungsfrist: **9. November 2026, 09:00 GMT**; Gewinnerbekanntgabe: 13. November 2026.
- Für die Wertung zählt Celo **Mainnet**; Testnet-Transaktionen zählen nicht.
- Der Event-Attribution-Tag muss vor der ersten relevanten Transaktion eingebaut sein und jede wertbare Transaktion begleiten.
- Agent-Wallet dem Event-Eintrag hinzufügen und deren ERC-8004-Identität vor Frist aus genau dieser Wallet registrieren.
- Bei Anmeldung ist ein **öffentliches GitHub-Quellcode-Repository** anzugeben, das zur Bewertung erreichbar bleibt.
- Die Regeln sagen, der Code werde während des Hackathons geschrieben. Für ein bereits begonnenes Projekt die Zulässigkeit mit dem Veranstalter klären.
- Mögliche Richtungen: `Build with buy` verlangt passende Bezahlung externer Leistungen; `USA₮ with x402` verlangt reale Mainnet-Abwicklung mit USA₮. Der aktuelle Sepolia-/Test-USDC-Flow erfüllt dies nicht.

Satya war im geprüften Stand **nicht einreichungsbereit**: kein dokumentierter Mainnet-Beitrag, kein nachgewiesener Attribution-Tag, keine bestätigte ERC-8004-Verknüpfung mit dem Event-Eintrag und kein öffentliches Satya-Quellcode-Repository. Das private Gesprächsarchiv schließt diese Source-Code- und Hackathon-Lücken nicht.

## Nächste Schritte für zukünftige KI-Sitzungen

1. Vor Implementierungen aktuellen Quellcode, Deployments, Chain-Daten und Nutzerwünsche erneut prüfen; dieses Archiv ist ein zeitgebundener Kontext, keine unveränderliche Spezifikation.
2. Vor Mainnet Nullifier-Linkability/Datenschutz untersuchen und gegebenenfalls das On-chain-Datenmodell ändern.
3. SBT erst nach separater Freigabe auf einer gewählten Chain deployen und Mint/Recovery/Expiry im Frontend integrieren.
4. x402-Backend erst mit vollständiger Runtime-Konfiguration starten; keine Zahlung, Wallet-Signatur oder Transaktion ohne die jeweils erforderliche Nutzerfreigabe.
5. Vor Hackathon-Einreichung Track-Fit und vorhandene Codebasis mit dem Veranstalter klären; Attribution Tag, ERC-8004-Verknüpfung und Mainnet-Nachweise erbringen.
6. Dieses private Kontextarchiv nicht ohne neue Freigabe öffentlich spiegeln. Eine separate öffentliche Source-Code-Veröffentlichung braucht ein festgelegtes Ziel und die Prüfung der genauen Dateien.
