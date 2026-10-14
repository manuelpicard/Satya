# Satya — Modulübersicht und Vollständigkeitsprüfung

**Prüfstand:** 14. Oktober 2026
**Basis:** lokale Satya-Quellbäume, README-Dateien, Quellmodule und Tests; kein Code wurde mit diesem Kontextarchiv veröffentlicht.

## 1. Wo der Code liegt — und was dieses GitHub-Repository enthält

- `manuelpicard/Satya` ist das private **Kontextarchiv**. Es enthält `projects/satya/` mit Dokumentation, aber nicht die App-, Python- oder Solidity-Quellen.
- Die Git-Arbeitskopie `satya-agent/` enthält die Next.js-dApp, Solidity-Contracts, Demo-Aufnahme-Skripte und Dokumentation. Der geprüfte lokale Commit lautet `46fdf39` (`Add soulbound human credential and hackathon readiness`); für diese Arbeitskopie war kein GitHub-Remote konfiguriert.
- Das Python-Paket liegt in einem separaten lokalen Baum `satya/`, nicht in diesem GitHub-Repository. Der Python-Projektbaum ist kein Git-Arbeitsbaum. Dort wird `contracts/` über den Symlink auf `satya-agent/contracts/` bereitgestellt.
- **Folge für eine neue KI:** Dieses private Repo liefert vollständigen Projektkontext, aber keinen baubaren Source-Checkout. Die genannten lokalen Quellpfade und den tatsächlichen aktuellen Code vor Änderungen erneut prüfen.

## 2. Python-Engine und HTTP-API (`satya/`)

| Modul/Pfad | Verantwortung | Vertrauensgrenze / Status |
|---|---|---|
| `satya/engine.py` | Orchestriert Datei-/Textprüfung, C2PA, Metadaten, Wasserzeichen, optionale Signatur und Register; baut Ergebnis aus Belegen auf. | Informations-/Hinweise werden nicht mit Beweisen verwechselt. Kein statistischer Stil-Detektor für Texte. |
| `satya/model.py`, `satya/verdict.py` | Typen `Evidence`, `Tier`, `Direction`, `Verdict`, `Result` und reine, deterministische Urteilslogik. | Nur `Tier.PROOF` kann ein sicheres Urteil tragen; `HINT` kann es nicht ändern. Widersprüchliche Beweise ergeben Widerspruch, fehlende Beweise `UNBESTIMMT`. |
| `satya/hashing.py` | Textnormalisierung `satya-text-v1`, SHA-256, Entfernen/Erkennen unsichtbarer Zeichen, pHash für Bilder, SimHash und Distanz. | Exakte Hashes binden Aussagen an Bytes/Text; weiche Ähnlichkeit ist nur ein Suchhinweis, kein Herkunftsbeweis. |
| `satya/c2pa_check.py`, `satya/trust/*` | C2PA-Manifeste und Signaturen samt MIME-Erkennung und eingebundener Zertifikats-/TSA-Vertrauenslisten prüfen. | Nur passende Signaturen von vertrauenswürdigen Ausstellern können Beweisstatus erreichen. Vertrauenslisten aktuell halten. |
| `satya/metadata_check.py`, `satya/watermark_check.py` | Metadaten- und Wasserzeichen-Indizien; optionale Provider-Detektoren. | Indizien sind keine Gewissheit: Metadaten/Wasserzeichen lassen sich entfernen oder fälschen. Keine generelle KI-Erkennung. |
| `satya/seal.py` | EIP-712-Siegel serialisieren, signieren, aus Text extrahieren und Signierer verifizieren. Siegel tragen Hash, Ursprungsaussage, Zeit, Signierer, Chain und Register. | Signatur beweist, wer eine Erklärung abgegeben hat; nicht, dass sie wahr ist. Bei fehlendem/falschem Register kann der Menschstatus nur Hinweis sein. |
| `satya/ledger.py`, `satya/abi/*` | `SatyaRegistry`-/HMN-Adapter: Erklärungen, Provider, Siegel und Validität abfragen; Hash-/Seal-Belege bilden. | Älterer HMN-/`HumanCredential`-Pfad; nicht mit dem ownerless Self-/ERC-8004-Contract `SatyaCelo` verwechseln. |
| `satya/celo_ledger.py` | Read-only-Adapter für `SatyaCelo`; liest Statements, Zusammenfassung, Self Agent ID und ERC-8004-Konfiguration aus Celo. | Kürzt Personen-Nullifier in seiner JSON-Ausgabe, aber die vollständigen Nullifier sind auf der öffentlichen Chain weiterhin lesbar (siehe Datenschutz-Hinweis unten). |
| `satya/cli.py`, `satya/__main__.py` | CLI-Kommandos `pruefen`, `siegeln`, `verankern`, `status`. | `SATYA_KEY` ist ein lokaler Signierschlüssel-Input, kein Frontend-Secret; niemals Schlüssel protokollieren oder committen. |
| `satya/server.py` | FastAPI-Web-UI/API: `POST /api/pruefen`, `/api/beispiele`, `/api/celo/status`, `/api/celo/herkunft/{hash}`, `/.well-known/agent.json`, `POST /api/x402/verify`; zusätzlich Demo-Endpoint `/api/demo/siegeln`. | Datei-Upload auf 50 MB begrenzt. Demo-Siegel nur bei expliziter Demo-Konfiguration; nicht produktiv verwenden. |
| `satya/x402.py` | x402-Gateway: 402-Angebot, Zahlungsnachweis, Abrechnung/Receipt und Agent-Card. | EIP-3009-/Facilitator-Zahlungsweg pro Anfrage. Im letzten lokalen Starttest waren Celo und x402 nicht konfiguriert; Endpoint nicht einsatzbereit, bis Runtime-Konfiguration vorliegt. |

**Tests:** `tests/test_verdict.py`, `tests/test_hashing_seal.py`, `tests/test_media.py`; 20/20 Python-Tests bestanden. Die lokalen Python-Dateien und Tests sind nicht in `manuelpicard/Satya` eingecheckt.

## 3. Solidity-Contracts (`satya-agent/contracts/`)

| Modul/Pfad | Verantwortung | Status / Abgrenzung |
|---|---|---|
| `src/SatyaCelo.sol` | Aktueller, ownerless Provenienzvertrag: Self-Human-, Self-Agent- und ERC-8004-Erklärungen, EIP-712-Seal-Ankerung, Widerruf, Abfragen und On-chain-Nachweis einer Selbstwidersprüchlichkeit. Ein Self-/Mensch-Nullifier begrenzt Erklärungen pro Person/Inhalt. | ERC-8004-Agenten können nur `AI_GENERATED` erklären, nicht menschliche Urheberschaft. `softHash` dient allein der Ähnlichkeitssuche. Sepolia-Deployment ist verifiziert; Adresse siehe Handoff. |
| `src/SatyaRegistry.sol` | Ältere HMN-Registry für Menschenaussagen und registrierte KI-Provider, EIP-712-Siegel, Widerruf und Fraud-Markierung. | `Ownable2Step`: Provider- und Fraud-Governance unterscheidet sich bewusst vom ownerless `SatyaCelo`. Nicht als identischer aktueller Registry-Pfad dokumentieren. |
| `src/credentials/SatyaHumanSBT.sol` | ERC-721 + ERC-5192 Soulbound Human Credential mit Claim/Refresh, Ablaufprüfung, Recovery derselben Self-Person und Renounce/Burn. | Noch nicht deployed und nicht in die Frontend-Oberfläche integriert. Es beweist keine Inhaltsautorenschaft. |
| `src/interfaces/*` | `ISelfAgentRegistry`, `IIdentityRegistry8004`, `IHumanRegistry`, `IERC5192`. | Externe Identitäts-/SBT-Schnittstellen; Vertrauensannahmen und Chain-Adressen müssen zum Deployment passen. |
| `test/*`, `test/mocks/*` | Tests für beide Register, Credential, Self-/ERC-8004-Prüfungen, Widerspruch, Revocation, Signaturen und Mock-Human-Registry. | 60/60 Foundry-Tests bestanden: 29 `SatyaCelo`, 17 `SatyaRegistry`, 14 `SatyaHumanSBT`. |
| `script/DeployCelo.s.sol`, `script/DeploySatyaHumanSBT.s.sol` | Deployment-Skripte für Registry und SBT. | SBT-Skript ist ausdrücklich Sepolia-only; in dieser Arbeit wurde kein SBT-Deployment ausgelöst. |
| `.gitmodules`, `lib/*` | Gepinnte OpenZeppelin- und forge-std-Abhängigkeiten. | OpenZeppelin `v5.7.0`, forge-std `v1.17.0`; nach Clone `git submodule update --init --recursive`. |

### Wichtiger Nullifier-Datenschutzhinweis (bei der Prüfung entdeckt)

Die ursprüngliche Handoff-Fassung sagte fälschlich, die Contract-API gebe den Nullifier nicht über Getter/Event preis. Das trifft **nicht** auf `SatyaCelo` zu: Event `Declared` enthält den vollen Nullifier; `attestation(s)` und `humanBehind()` liefern ihn ebenfalls. `celo_ledger.py` kürzt ihn nur für seine JSON-Antwort, nicht für die Blockchain. Auch `SatyaRegistry` veröffentlicht eine HMN-`personId` in Attestationsdaten/Events. `SatyaHumanSBT` emittiert/returniert den Nullifier nicht über ein dediziertes API, aber Contract-Storage ist auf einer EVM-Chain grundsätzlich öffentlich lesbar. Daher besteht keine Anonymitätsgarantie; vor Mainnet ist eine gezielte Datenschutz- und Linkability-Prüfung nötig.

## 4. Next.js-dApp (`satya-agent/app/`)

- `page.tsx`, `components/SatyaAgent.tsx`: Start-/Dashboard-UI; Auswahl von Datei/Text, Anzeige der Hash- und Registerbefunde.
- `lib/celo.ts`: Celo-Sepolia-Chain, Contract-/Self-Adressen, Textnormalisierung und Browser-SHA-256.
- `components/WalletPanel.tsx`: EIP-1193-Wallet, Wechsel zu Celo Sepolia, Self Agent ID/Frische- und Wallet-Checks; Signatur/Transaktion bleibt beim Nutzer. Human-Erklärung erfolgt über `declareAsHuman`.
- `components/X402Panel.tsx`: Preisabfrage ohne Datei/Text zu übertragen; Betrag, Asset, Netzwerk und Empfänger werden vor einer getrennten EIP-3009-Autorisierung angezeigt. Erst danach wird der ausgewählte Inhalt an den Prüfdienst geschickt.
- `app/api/satya/route.ts`, `app/api/x402/route.ts`: Next.js-Endpunkte/Proxy für Register- und x402-Backend-Anfragen; kein Fallback, der heimlich eine Zahlung auslöst.
- Browser-Hashing unterstützt Dateien bis 50 MB; Text wird zu `satya-text-v1` normalisiert. Standard ist Sepolia/Test-USDC, kein Mainnet-Zahlungsprodukt.
- SBT-Mint-/Recovery-UI fehlt, solange das Credential nicht deployed ist.

## 5. Demo, Messung und Sicherheitsgrenzen

- Python-Demo: `demo/serve.sh`, `run_demo.sh`, `celo_flow.py`, `x402_client.py`, `evaluate.py`, `build_corpus.py`, `seed_chain.py`, `c2pa_sign.py`, `make_demo_ca.py`, `generate_ai_texts.py`.
- Das Demo-Korpus umfasst 22 Fälle (Bilder, Kamera-/C2PA-Metadaten, Textsiege, Manipulationen, Paraphrasen und Widersprüche). Die dokumentierte Stichprobe ergab 9 sichere Urteile, davon ein falsches; im kleinen Korpus wurden keine echten menschlichen Inhalte fälschlich als KI eingestuft. Das ist ein **begrenzter interner Test**, keine generalisierbare Genauigkeitsgarantie.
- `satya-agent/scripts/record_demo.py` und `render_demo_video.py` erzeugen den 16,6-Sekunden-Demo-Clip samt deutschen Untertiteln. Die Aufnahme löst keine Wallet-Signatur oder Zahlung aus.
- Im separaten Demo-Quellbaum gibt es ausdrücklich lokale Demo-CA-/Anvil-Schlüsselmaterialien (`demo/pki/` und Demo-Key-Konfiguration in `server.py`). Sie sind ausschließlich für die lokale Demonstration bestimmt; **ihre Werte gehören nicht in dieses Archiv und dürfen nie produktiv verwendet werden**.
- Vor Produktiv-/Mainnet-Einsatz sind externer Contract-Audit, Datenschutzreview und sichere Trennung aller Demo-Schlüssel nötig.

## 6. Aktuelle Deployments und Verifikation

- Celo Sepolia Chain ID `11142220`; `SatyaCelo` `0x58d5f2c2ac866D7828b7e2Bf1A3542C3536c3001`.
- Self Agent ID Registry `0x043DaCac8b0771DD5b444bCC88f2f8BBDBEdd379`.
- ERC-8004 Sepolia Registry `0x8004A818BFB912233c491871b3d84c89A494BD9e`; Satya-Agent-ID laut Python-README `453`.
- x402-Test-USDC `0x01C5C0122039549AD1493B8220cABEdD739BC44E`; frühere Entwicklungsnotizen verzeichnen Testnet-Abwicklung, aber der letzte lokale Backendstart war ohne X402-/Celo-Konfiguration.
- `SatyaHumanSBT`: keine Deploy-Adresse. Kein Mainnet-Deployment, kein Mainnet-Zahlungsfluss und kein Hackathon-Attribution-Tag sind durch den geprüften Projektstand belegt.

## 7. Audit-Fazit

Die vorherige Gesprächsnotiz deckte Produktziel, Kernarchitektur, Tests und Hackathon-Status ab, aber nicht alle zentralen Module oder deren Grenzen. Diese Datei ergänzt die vollständige wichtige Modulkarte und korrigiert insbesondere die Nullifier-Aussage. Das Kontextarchiv ist damit für spätere KI-Sitzungen deutlich vollständiger; es ersetzt weiterhin nicht den Quellcode und muss bei Änderungen an Code, Chain oder Eventregeln aktualisiert werden.
