# Satya — aktuelles KI-Handoff (1. November 2026)

Dieses Dokument ergänzt `conversation-handoff.md`, die Modulkarte und die am 31. Oktober angelegten Hackathon-Notizen. Es bündelt die letzten Arbeitsschritte aus der Sandbox für eine Fortsetzung mit einer anderen KI. Das Repository ist privat. Dieses Handoff ist eine kuratierte Übergabe, kein wortgetreues Volltranskript.

## Kurzfassung

Satya ist als **Provenienz- und Rechenschaftssystem** zu behandeln, nicht als universeller KI-Detektor. Ein kryptografischer Beleg kann eine signierte Aussage oder Herkunftsbindung belegen; ohne passenden Beleg muss Satya `unbestimmt` sagen. Das Ziel ist die Teilnahme am Celo-Hackathon „Agents on Open Rails“. Privatsphäre des Self-Nullifiers, ERC-8021-Attribution, x402-Abwicklung und fehlende Mainnet-Evidenz bleiben offene Themen.

## Wo ist der vollständige Quellcode?

Der vollständige bereinigte Stand ist jetzt im privaten Repository unter [`../source/2026-11-01/`](../source/2026-11-01/README.md) abgelegt. Dort befinden sich beide ursprünglichen Projektwurzeln: `satya-agent/` (Next.js-Frontend, Solidity-Contracts, Foundry-Tests und Skripte) sowie `satya/` (Python-Engine/FastAPI, Tests, Web-UI und Demo). Die Sandbox-Kopien lagen zuvor unter `/home/ubuntu/satya-hackathon-work/satya-agent/` und `/home/ubuntu/satya-hackathon-work/satya/`; diese Pfade sind keine Git-Repositories. Die ältere `/home/ubuntu/satya-agent-celo.zip` war ein lokales Hand-off-Archiv.

Der GitHub-Snapshot ist eine datierte Kopie ohne die Git-Historie bzw. Remote-Konfiguration des ursprünglichen Quellprojekts. Er lässt `node_modules`, `.next`, Python-/Foundry-Caches, lokale `.env`-Dateien, `*.key`-Demo-Privatschlüssel und lokale Chain-State-Dateien aus. Einzelheiten stehen in `source/2026-11-01/README.md`. `server.py` enthält feststehende, öffentlich bekannte Anvil-Entwicklungsschlüssel, nur für die lokale Demo; sie sind keine Produktionsschlüssel und dürfen nie mit echten Mitteln oder auf Mainnet verwendet werden.

`work-in-progress/2026-11-01/` bleibt als kleinere Ablage der zentralen geänderten Dateien erhalten; sie ist nur ein schneller Vergleichs-/Reviewbereich. Für die Fortsetzung ist der vollständige `source/2026-11-01/`-Baum die bessere Einstiegskopie.

## Bereits im Repository vorhandene Projektunterlagen

- `context/conversation-handoff.md`: vorherige kuratierte Projekterinnerung.
- `context/module-inventory.md`: Modulübersicht samt bekannten technischen und Datenschutzgrenzen.
- `context/hackathon-plan.md`, `context/mainnet-research.md`, `context/submission-draft.md`: Hackathon-Arbeit, zuletzt aktualisiert bis 31. Oktober. Vor einer Einreichung Regeln und Fristen live erneut prüfen.

## Was im zuletzt übernommenen Code geändert wurde

1. **ERC-8021-Suffix:** neues Python-Modul `satya/attribution.py` für ein CBOR-basiertes Rollen-Suffix. Der Frontend-Code nutzt `@celo/attribution-tags` und versieht Wallet-Writes mit `withAttribution`. Ohne `NEXT_PUBLIC_CELO_ATTRIBUTION_CODE` wird die Deklaration absichtlich gesperrt. Den offiziellen Loops-/Celo-App-Code nicht raten oder erfinden; beim Hackathon-Betreiber verifizieren.
2. **x402-/Celo-Assets:** Entwurf `satya/x402.py` ergänzt Celo-Sepolia-USDC und Celo-Mainnet-USA₮ aus der live gelesenen Facilitator-`/supported`-Liste. USA₮ wurde dabei mit Adresse `0xD2ab3C9A02DBBAB236BfEC45D1d755DF4267F771` und EIP-3009-Metadaten (`USAT`, 6 decimals, Domain-Version `1`) erfasst. Vor Verwendung die aktuelle Facilitator-Liste erneut abfragen.
3. **Settlement-Schutz:** der Backendentwurf versucht EIP-3009 zu verifizieren und zu begleichen; ein Ergebnis soll erst nach erfolgreichem Receipt und passendem ERC-20-`Transfer`-Log ausgegeben werden. Die Frontend-Quote zeigt Netzwerk, Token, Betrag und Empfänger; für Mainnet ist `NEXT_PUBLIC_SATYA_MAINNET_X402` standardmäßig aus, und eine lokal konfigurierte Empfänger-Allowlist wird verlangt. Das ist noch kein produktionsgeprüfter Zahlungsfluss.
4. **Dependencies/Sicherheit:** `satya-agent/package.json` und Lockfile enthalten `@celo/attribution-tags` und damalige Next.js-/PostCSS-Pins. Readiness- und Security-Notizen sind im Frontend-Snapshot unter `docs/` archiviert.

## Prüfstatus und Grenzen

- `npx tsc --noEmit`: bestanden.
- `npm run build`: Next.js-Produktionsbuild bestanden (Next.js 15.5.28).
- `npm audit --omit=dev`: zuvor mit 0 Findings gemeldet; vollständigen Audit beim nächsten Build erneut ausführen.
- `python3 -m py_compile satya/attribution.py satya/x402.py satya/server.py`: bestanden.
- Python-Tests wurden **nicht** ausgeführt: in dieser Sandbox fehlte `pytest`. Nicht als bestandene Tests ausgeben.
- Ältere Projektunterlagen dokumentieren 60/60 Foundry- und 20/20 Python-Tests für einen damaligen Quellstand; das beweist nicht, dass die jetzigen x402-Entwürfe integriert oder getestet sind.
- Es wurde in dieser letzten Arbeitsrunde kein Wallet-Signaturdialog bestätigt, kein Settlement gesendet, kein Mainnet genutzt und kein Contract deployed.

## Kritische Review-Punkte vor Übernahme

1. `satya/x402.py` enthält noch `allow_untagged_mainnet` / `X402_ALLOW_UNTAGGED_MAINNET` als Betreiber-Override. Vor Mainnet klären, ob diese Ausnahme vollständig entfernt werden muss; voreingestellt ist sie aus, aber sie bleibt eine explizite Fail-open-Möglichkeit.
2. Laut Celo-Dokumentation ist Facilitator-seitiges Tagging von x402-Settlements nicht live. Der gehostete `/settle`-Pfad liefert daher nicht automatisch den ERC-8021-Beleg. Die vorgeschlagene direkte Relayer-Route muss separat gegen x402-Version, Signatur-Domain, EIP-3009-Vertrag, Celo-RPC, Fehler-/Nonce-Verhalten und Attribution geprüft werden.
3. FastAPI führt die Analyse im Entwurf vor dem Settlement aus und hält das Resultat erst danach zurück. Das kann bei fehlgeschlagenen Settlements unnötige Rechenlast erlauben; Reihenfolge und Replay-/Idempotenzbehandlung reviewen.
4. Es fehlen Python-Unit-/Integrationstests für CBOR-Vektoren, Quote-Validierung, Verifikation, Settlement-RPC, Revert/Timeout, Transfer-Log-Parser, Mainnet-Attribution und Ergebnisfreigabe. Contract-/Backend-Tests ergänzen.
5. Versions-/Schema-Kompatibilität zwischen der x402-v1-Implementierung, möglichen v2-Payloads und dem gehosteten Facilitator prüfen. Keine echte Zahlung vor End-to-End-Testnet-Integration einsetzen.
6. Der Source-Snapshot ist keine versionierte Arbeitskopie. Für Änderungen daraus eine frische, versionierte Arbeitskopie erstellen und nicht direkt in den Archivordner entwickeln.

## Empfohlene Reihenfolge für die nächste KI

1. Dieses Dokument sowie `README.md`, `context/module-inventory.md`, `context/hackathon-plan.md`, `context/mainnet-research.md` und `context/submission-draft.md` lesen.
2. Den vollständigen Code unter `source/2026-11-01/` lesen; keine ausgelassenen Builddaten oder Schlüssel aus der Sandbox voraussetzen.
3. `allow_untagged_mainnet` entfernen oder präzise begründen; Backendtests ergänzen; Python-Abhängigkeiten gemäß Manifest isoliert installieren und Tests ausführen.
4. Celo-Sepolia-x402 end-to-end mit Test-USDC und tatsächlichem Settlement-Beleg testen; anschließend App-/Wallet-Rollencodes bei Loops/Celo verifizieren.
5. Änderungen nach Review in das eigentliche Source-Repository übertragen. Hackathon-Einreichung, Mainnet-Zahlung, Wallet-Signatur und öffentliche Veröffentlichung weiterhin nur mit separater Nutzerfreigabe.

## Korrekte Aussagen nach außen

- Keine Behauptung, Satya könne jeden KI-Inhalt „todsicher“ erkennen.
- Celo Sepolia: die dokumentierte bestehende `SatyaCelo`-Adresse steht im älteren Handoff; für das ERC-5192-SBT gibt es dort bisher keine bestätigte Deployment-Adresse.
- Die USA₮-Adresse/Unterstützung belegt weder eine Satya-Mainnet-Integration noch einen erfolgten Mainnet-Transfer.
- Das private Handoff und der Quellcode-Snapshot sind weder Hackathon-Einreichung noch Code-Audit oder Deployment.
