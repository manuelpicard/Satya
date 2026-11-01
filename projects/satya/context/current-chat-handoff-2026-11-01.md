# Satya — aktuelles KI-Handoff (1. November 2026)

Dieses Dokument ergänzt `conversation-handoff.md`, die Modulkarte und die am 31. Oktober angelegten Hackathon-Notizen. Es bündelt die letzten Arbeitsschritte aus der Sandbox für eine Fortsetzung mit einer anderen KI. Das Repository ist privat. Dieses Handoff ist eine kuratierte Übergabe, kein wortgetreues Volltranskript.

## Kurzfassung

Satya ist als **Provenienz- und Rechenschaftssystem** zu behandeln, nicht als universeller KI-Detektor. Ein kryptografischer Beleg kann eine signierte Aussage oder Herkunftsbindung belegen; ohne passenden Beleg muss Satya `unbestimmt` sagen. Das Ziel ist die Teilnahme am Celo-Hackathon „Agents on Open Rails“. Privatsphäre des Self-Nullifiers, ERC-8021-Attribution, x402-Abwicklung und fehlende Mainnet-Evidenz sind wichtige offene Themen.

Am 26. Oktober wurde in einer aus dem ZIP wiederhergestellten lokalen Arbeitskopie an Celo-Attribution und x402-Sicherheit gearbeitet. Die geänderten Dateien sind **als unverifizierte Arbeitsentwürfe**, nicht als freigegebene Produktionsquellen, unter `projects/satya/work-in-progress/2026-11-01/` abgelegt. Das dortige Verzeichnis enthält Pfad-nachgebildete Snapshots aus zwei getrennten lokalen Quellbäumen. Es enthält absichtlich weder `node_modules` noch `.env`, Schlüssel oder Wallet-Geheimnisse.

## Bereits im Repository vorhanden

- `context/conversation-handoff.md`: vorherige kuratierte Projekterinnerung.
- `context/module-inventory.md`: Modulübersicht samt bekannten technischen und Datenschutzgrenzen.
- `context/hackathon-plan.md`, `context/mainnet-research.md`, `context/submission-draft.md`: jüngere Hackathon-Arbeit, zuletzt aktualisiert bis 31. Oktober. Vor einer Einreichung Regeln/Fristen erneut live prüfen.
- `work-in-progress/2026-11-01/`: exakte Quelltext-Snapshots der jüngsten Frontend-/Backendversuche und zugehörige Paketdateien/Dokumente.

## Was im lokalen Entwurf geändert wurde

1. **ERC-8021-Suffix:** neues Python-Modul `backend/satya/attribution.py` für ein CBOR-basiertes Rollen-Suffix. Der Frontend-Entwurf nutzt `@celo/attribution-tags` und versieht Wallet-Writes mit `withAttribution`. Ohne `NEXT_PUBLIC_CELO_ATTRIBUTION_CODE` wird die Deklaration absichtlich gesperrt. Den offiziellen Loops-/Celo-App-Code nicht raten oder erfinden; beim Hackathon-Betreiber verifizieren.
2. **x402-/Celo-Assets:** Entwurf `backend/satya/x402.py` ergänzt Celo-Sepolia-USDC und Celo-Mainnet-USA₮ aus der live gelesenen Facilitator-`/supported`-Liste. USA₮ wurde dabei mit Adresse `0xD2ab3C9A02DBBAB236BfEC45D1d755DF4267F771` und EIP-3009-Metadaten (`USAT`, 6 decimals, Domain-Version `1`) erfasst. Vor Verwendung die aktuelle Facilitator-Liste erneut abfragen.
3. **Settlement-Schutz:** der Backendentwurf versucht EIP-3009 zu verifizieren und zu begleichen; ein Ergebnis soll erst nach erfolgreichem Receipt und passendem ERC-20-`Transfer`-Log ausgegeben werden. Die Frontend-Quote zeigt Netzwerk, Token, Betrag und Empfänger; für Mainnet ist `NEXT_PUBLIC_SATYA_MAINNET_X402` standardmäßig aus, und eine lokal konfigurierte Empfänger-Allowlist wird verlangt. Das ist noch kein produktionsgeprüfter Zahlungsfluss.
4. **Security-baseline:** `frontend/package.json` und `package-lock.json` enthalten `@celo/attribution-tags` sowie damalige Next.js-/PostCSS-Dependency-Pins. Die zugehörige Baseline und Readiness-Notiz liegen unter `frontend/docs/`.

## Verifizierter Arbeitsstand / Grenzen der Tests

- `npx tsc --noEmit`: bestanden.
- `npm run build`: Next.js-Produktionsbuild bestanden (Next.js 15.5.28).
- `npm audit --omit=dev`: zuvor mit 0 Findings gemeldet; vollständigen Audit beim nächsten Build erneut ausführen.
- `python3 -m py_compile satya/attribution.py satya/x402.py satya/server.py`: bestanden.
- Python-Tests wurden **nicht** ausgeführt: in dieser Sandbox fehlt das Modul `pytest`. Nicht als bestandene Tests ausgeben.
- Frühere Projektunterlagen dokumentieren 60/60 Foundry- und 20/20 Python-Tests für einen damaligen Quellstand; das beweist nicht, dass die jetzigen x402-Entwürfe integriert oder getestet sind.
- Es wurde in dieser letzten Arbeitsrunde kein Wallet-Signaturdialog bestätigt, kein Settlement gesendet, kein Mainnet genutzt und kein Contract deployed.

## Kritische Review-Punkte vor Übernahme

1. `backend/satya/x402.py` enthält noch `allow_untagged_mainnet` / `X402_ALLOW_UNTAGGED_MAINNET` als Betreiber-Override. Vor Mainnet muss geklärt werden, ob diese Ausnahme vollständig entfernt werden soll; voreingestellt ist sie aus, aber sie ist eine explizite Fail-open-Möglichkeit.
2. Laut Celo-Dokumentation ist Facilitator-seitiges Tagging von x402-Settlements nicht live. Der gehostete `/settle`-Pfad liefert daher nicht automatisch den ERC-8021-Beleg. Die vorgeschlagene direkte Relayer-Route muss separat gegen x402-Version, Signatur-Domain, EIP-3009-Vertrag, Celo-RPC, Fehler-/Nonce-Verhalten und Attribution geprüft werden.
3. FastAPI führt die Analyse im Entwurf vor dem Settlement aus und hält das Resultat erst danach zurück. Das kann bei ungültigen/fehlgeschlagenen Settlements unnötige Rechenlast erlauben; die Reihenfolge und Replay-/Idempotenzbehandlung reviewen.
4. Es fehlen Python-Unit-/Integrationstests für CBOR-Vektoren, Quote-Validierung, Verifikation, Settlement-RPC, Revert/Timeout, Transfer-Log-Parser, Mainnet-Attribution und Ergebnisfreigabe. Contract-/Backend-Tests gezielt ergänzen.
5. Versions-/Schema-Kompatibilität zwischen der vorhandenen x402-v1-Implementierung, möglichen v2-Payloads und dem gehosteten Facilitator prüfen. Keine echte Zahlung einsetzen, bevor Testnet-Integration end-to-end besteht.
6. Die Sandbox-Arbeitskopien unter `/home/ubuntu/satya-hackathon-work/` waren keine Git-Repositories. Die archivierten Snapshots sind deshalb ein Übergabe-Artefakt, kein sauberer Source-Branch oder Patch gegen eine eindeutig gepinnte Basis. Beim nächsten Schritt zunächst in einer frischen, versionierten Arbeitskopie eine Integration/Review durchführen.
7. Kein offizieller ERC-8021-App-Code, x402-API-Key, Relayer-Key, Wallet-Geheimnis oder Mainnet-Pay-to-Wert wurde in diese Handoff-Dateien aufgenommen.

## Empfohlene Reihenfolge für die nächste KI

1. Dieses Handoff sowie `README.md`, `context/module-inventory.md`, `context/hackathon-plan.md`, `context/mainnet-research.md` und `context/submission-draft.md` lesen.
2. Die Dateien in `work-in-progress/2026-11-01/` als Vorschläge prüfen und gegen eine frische, gepinnte Projektquelle diffen; sie nicht blind als kanonischen Code übernehmen.
3. `allow_untagged_mainnet` entfernen oder präzise begründen; Backendtests mit Mocks schreiben; Python-Dependencies gemäß Projektmanifest in isolierter Umgebung installieren und Tests ausführen.
4. Celo-Sepolia-x402 end-to-end mit Test-USDC und einem tatsächlichen Settlement-Beleg testen; dann die exakten App-/Wallet-Rollencodes bei Loops/Celo verifizieren.
5. Erst nach Review die finale Änderung in das eigentliche Source-Repository übertragen. Einreichung, Mainnet-Zahlung, Wallet-Signatur und öffentliche Veröffentlichung weiterhin nur mit separater Nutzerfreigabe.

## Korrekte Aussagen nach außen

- Keine Behauptung, Satya könne jeden KI-Inhalt „todsicher“ erkennen.
- Celo Sepolia: dokumentierte bestehende `SatyaCelo`-Adresse steht im bestehenden Handoff; das ERC-5192-SBT hatte dort bisher keine bestätigte Deployment-Adresse.
- Die USA₮-Adresse/Unterstützung betrifft die aktuelle Facilitator-Liste; sie beweist weder eine Satya-Mainnet-Integration noch einen bereits erfolgten Mainnet-Transfer.
- Ein hochgeladenes privates Handoff ist weder Hackathon-Einreichung noch Code-Audit oder Deployment.
