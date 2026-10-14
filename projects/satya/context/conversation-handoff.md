# Satya — Projekt- und Konversationskontext für zukünftige KI-Sitzungen

**Stand:** 14. Oktober 2026
**Zweck:** Dauerhafte, weiterverwendbare Übergabe zu Satya: Nutzerziele, Entscheidungen, Architektur, verifizierter Projektstand, Grenzen und nächste Schritte.

> **Archivhinweis:** Dies ist eine kuratierte Projekterinnerung aus dem in der aktuellen Sitzung verfügbaren Verlauf. Frühere Gesprächsteile wurden beim Sitzungswechsel zusammengefasst; daher ist dies kein wortgetreues Volltranskript aller historischen Assistentenantworten. Verfügbare ursprüngliche Nutzerformulierungen sind unten erhalten. Interne System-/Entwicklerinstruktionen, Zugangsdaten, persönliche Wallet-Schlüssel und private Tooldaten gehören nicht in dieses öffentliche Archiv.

## Projektziel und feste Produktgrenzen

Satya ist ein Celo-basiertes System zur nachvollziehbaren Herkunftserklärung von digitalen Inhalten. Es soll prüfbare, signierte Aussagen an einen Content-Hash binden und bei Bedarf pro Anfrage bezahlte Prüfungen über x402 bereitstellen. Der Schwerpunkt ist **Provenienz und Rechenschaft**, nicht ein universeller KI-Detektor.

Ein Ergebnis darf nur dann als **gewiss** dargestellt werden, wenn die dazugehörige Aussage bzw. der Identitäts- und Signaturbeweis kryptografisch geprüft wurde. Ohne passende, gültige Evidenz lautet das Ergebnis **unbestimmt**. Fehlende KI-Metadaten, fehlende C2PA-Angaben oder fehlende Registry-Einträge beweisen keine menschliche Urheberschaft. Ein Self-Proof belegt eine geprüfte menschliche Identität bzw. ein Proof-of-Personhood-Kriterium; für sich allein beweist er **nicht**, dass diese Person einen bestimmten Inhalt erstellt hat.

Keine Dokumentation, Demo oder Oberfläche darf versprechen, Satya könne zweifelsfrei feststellen, ob beliebiger Inhalt durch irgendeine KI entstanden ist. Signierte Herkunftserklärungen bleiben Aussagen ihrer Unterzeichner und sind nicht automatisch wahr.

## Nutzerentscheidungen und erhaltener Gesprächsverlauf

Die folgenden Formulierungen stammen aus den erhaltenen Nutzerbeiträgen. Die historische Reihenfolge ist erhalten; für frühere Beiträge sind nicht durchgängig Zeitstempel vorhanden.

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
19. Am 14. Oktober 2026: „in die Satya repo von manuelpicard“ — die Zielauswahl bezieht sich auf das private Repository `manuelpicard/Satya`.

Daraus abgeleitete, weitergeltende Nutzerwünsche: Projektname **Satya** (nicht Satyagiri); Celo als Blockchain-Ökosystem; ein Soulbound-Menschennachweis; Hackathon-Nutzung zur Umsetzung und Sichtbarkeit; keine „gewisse“ Herkunftsaussage ohne kryptografischen Beleg; ansonsten **unbestimmt**; Kommunikation mit dem Nutzer auf Deutsch.

## Architektur und aktueller Code

### Identität und Provenienz

- **Menschennachweis:** Self Agent ID / Self-Proof-of-Personhood mit frischem Proof und einem personenbezogenen Nullifier. Die Wallet muss den betreffenden Agent ID besitzen.
- **Provenienzregister:** Solidity-Verträge für signierte Ursprungserklärungen, AI-Agent-Erklärungen, Attester und Widersprüche. `SatyaCelo` unterstützt Self-Agent- und ERC-8004-Agentpfade. `SatyaRegistry` besitzt eigene Registry-Tests.
- **Soulbound Credential:** `contracts/src/credentials/SatyaHumanSBT.sol` implementiert ERC-5192. Der Contract erlaubt Claim/Refresh auf Basis eines frischen Self-Proofs, Ablaufprüfung, explizite Recovery auf eine andere Wallet derselben verifizierten Person sowie Renounce/Burn. Transfer und Approvals sind gesperrt. Dieses Credential belegt keinen Inhaltsautor.
- **Datenschutzprüfung vor Mainnet:** Das Contract-API exponiert den Nullifier nicht über einen Getter oder ein Event. Der Nullifier liegt aber in Contract-Storage; `private` in Solidity bedeutet keine Vertraulichkeit auf einer öffentlichen Chain. Die öffentliche Speicherung und Linkbarkeit sind vor Mainnet gesondert zu bewerten.
- **Frontend:** Next.js 15 / React 19 mit Viem; Datei-/Text-Hashing im Browser, Celo-Sepolia-Abfragen, Wallet-Verbindung und Self-Agent-Prüfung. Eine Wallet-Signatur bzw. Transaktion wird vom Nutzer selbst bestätigt.
- **Python-Engine/Backend:** Separater FastAPI-/Uvicorn-Projektbaum mit C2PA-, Metadaten-, Hash-, Siegel- und Verdict-Prüfungen sowie optionalem x402-Endpunkt. Der historische lokale Python-Testbestand hat 20 Tests.
- **x402:** Der frühere Entwicklungsstand dokumentiert erfolgreich erprobte Testnet-USDC-Zahlungen. Beim letzten Statuscheck war der lokale Dienst auf Port 8000 nicht aktiv. Ein temporärer lokaler Start funktionierte, gab aber `celo: null` und `x402: null` zurück, weil in dieser Umgebung keine entsprechende Runtime-Konfiguration vorlag. In der aktuellen Abschlussarbeit wurde keine Zahlung signiert oder ausgelöst.

### Netz und öffentlich bekannte Testnet-Adressen

- Celo Sepolia Chain ID: `11142220`
- `SatyaCelo`: `0x58d5f2c2ac866D7828b7e2Bf1A3542C3536c3001` (im früheren Projektstand als verifiziert auf Blockscout dokumentiert)
- Self Agent ID Registry: `0x043DaCac8b0771DD5b444bCC88f2f8BBDBEdd379`
- Test-USDC: `0x01C5C0122039549AD1493B8220cABEdD739BC44E`

Diese Werte beziehen sich auf Sepolia/Testnet. Test-Token haben keinen Mainnet-Wert. Keine Mainnet-Deployment-Adresse für `SatyaHumanSBT` ist dokumentiert.

### Repository- und Teststatus

- Der separate lokale Git-Arbeitsbaum `satya-agent` enthält App, `contracts/` und Docs. Sein Stand ist lokal committed unter `46fdf39` (`Add soulbound human credential and hackathon readiness`); in diesem Arbeitsbaum war kein GitHub-Remote konfiguriert. Dieser Commit wurde in der vorherigen Sitzung **nicht** zu GitHub gepusht.
- OpenZeppelin Contracts ist exakt auf `v5.7.0`, `forge-std` exakt auf `v1.17.0` gepinnt und in `.gitmodules`/Gitlinks festgelegt. `git submodule update --init --recursive` lädt die Abhängigkeiten nach einem Clone.
- Nach `forge clean` bestanden **60/60 Foundry-Tests**: 29 `SatyaCelo`, 17 `SatyaRegistry`, 14 `SatyaHumanSBT`.
- **20/20 Python-Tests** bestanden. Das vollständige Hand-off-ZIP wurde entpackt und die Foundry- sowie Python-Tests darin erneut erfolgreich ausgeführt.
- TypeScript-Prüfung und Next.js-Produktionsbuild waren im vorherigen Projektstand erfolgreich.
- Der Contract ist geschrieben und getestet, aber **noch nicht deployed** und noch **nicht** mit Mint-/Recovery-Aktionen im Frontend verbunden.
- Ein quellcodebereinigtes lokales Hand-off-ZIP wurde erzeugt. Zugangsdaten und `.secrets` gehören nicht in ein GitHub-Archiv.

## Hackathon: Agents on Open Rails

Offizielle Eventseite: <https://www.loops.house/agents-on-open-rails> (zuletzt geprüft am 12. Oktober 2026).

- Anmelde- und Einreichungsfrist: **9. November 2026, 09:00 GMT**; Gewinnerbekanntgabe: 13. November 2026.
- Für die Wertung zählt Celo **Mainnet**; Testnet-Transaktionen zählen nicht.
- Der vom Event-Eintrag ausgestellte Attribution Tag muss bereits vor der ersten relevanten Transaktion eingebaut sein und jede wertbare Transaktion begleiten.
- Agent-Wallet dem Event-Eintrag hinzufügen und deren ERC-8004-Identität vor der Frist aus genau dieser Wallet registrieren.
- Bei der Anmeldung ist ein **öffentliches GitHub-Repository** anzugeben, das während der Bewertung erreichbar bleibt.
- Die Eventregeln sagen, dass der Code während des Hackathons geschrieben wird. Bei einer vorhandenen Basis sollte die Zulässigkeit mit dem Veranstalter geklärt und die während des Hackathons entstandene Arbeit nachvollziehbar dokumentiert werden.
- Mögliche Richtungen: `Build with buy` erfordert die passende Integration, bei der der Agent für eine externe Leistung bezahlt; `USA₮ with x402` erfordert reale Mainnet-Abwicklung mit USA₮. Der bestehende Sepolia-/Test-USDC-Flow erfüllt das nicht.

Satya ist in diesem Zustand **nicht einreichungsbereit**: kein dokumentierter Mainnet-Beitrag, kein nachgewiesener Event-Attribution-Tag, keine bestätigte ERC-8004-Verknüpfung mit dem Event-Eintrag und kein öffentliches Satya-GitHub-Remote. Eine Veröffentlichung des Gesprächskontexts in `manualai.org` würde diese Source-Code- und Hackathon-Lücken nicht schließen.

## Nächste Schritte für zukünftige KI-Sitzungen

1. Vor jeder Implementierung den aktuellen Code, Deployments und Nutzerwünsche erneut prüfen; dieses Dokument ist Kontext, nicht unveränderliche Spezifikation.
2. Vor Mainnet entscheiden, ob der Nullifier-Storage mit den gewünschten Privacy-Eigenschaften vereinbar ist.
3. SBT auf einer ausdrücklich freigegebenen Chain deployen und Mint/Recovery/Expiry im Frontend integrieren; Deployment benötigt eine reale Wallet-Transaktion und ist nicht automatisch autorisiert.
4. x402-Backend erst nach Bereitstellung der erforderlichen Konfiguration starten; keine Zahlungs- oder Signaturaktion ohne separate Freigabe auslösen.
5. Für den Hackathon zuerst Track-Fit und Umgang mit bestehendem Code mit dem Veranstalter klären; Attribution Tag, ERC-8004-Verknüpfung, öffentliches Quellcodeziel und Mainnet-Nachweise vorbereiten.
6. Vor öffentlichem Push den genauen Zielpfad, die Sichtbarkeit und den tatsächlich veröffentlichten Inhalt prüfen. Diese Kontextnotiz veröffentlicht keinen Satya-Quellcode; das Source-Repository bleibt separat und hat kein konfiguriertes GitHub-Remote.
