# Satya-Quellcode — Snapshot vom 1. November 2026

Dies ist der vollständige, bereinigte Quellbaum für die Fortsetzung des Satya-Projekts. Er enthält zwei ursprünglich getrennte Projektwurzeln aus der Sandbox und ist im privaten Archiv unter `projects/satya/source/2026-11-01/` abgelegt.

## Aufbau

- `satya-agent/` — Next.js-/React-App, Solidity-Contracts und Foundry-Tests, Deploy-Skripte, Projekt-/Hackathon-Dokumente, statische Frontend-Assets und Demo-Skripte.
- `satya/` — Python-Engine, FastAPI-Server, Python-Tests, Trust-Listen, Web-UI sowie Demo-/Testkorpus.

Der Snapshot basiert auf den am 26. Oktober wiederhergestellten vollständigen Projektquellen und enthält die Änderungen dieser Sitzung bis 1. November. Dazu zählen die zuletzt bearbeiteten Dateien `satya-agent/app/components/WalletPanel.tsx`, `X402Panel.tsx`, `app/lib/celo.ts` sowie `satya/satya/attribution.py`, `x402.py` und `server.py`.

## Bereinigung und Grenzen

Ausgeschlossen wurden `node_modules`, `.next`, Foundry-Ausgaben/Cache, Python-Caches, lokale `.env`-Dateien, `*.key`-Dateien aus `satya/demo/pki/` sowie lokale `anvil-state.json`-/`celo_state.json`-Laufzeitstände. `.env.example`, Quellcode, Tests, Demo-Korpus und erforderliche Contract-Dependency-Dateien sind enthalten. Die Demo-Schlüsseldateien müssen bei Bedarf lokal neu erzeugt werden, zum Beispiel mit `satya/demo/make_demo_ca.py`; private Testschlüssel nicht committen.

`server.py` enthält feste, öffentlich bekannte Anvil-Entwicklungsschlüssel für die lokale Demo. Sie sind nur mit `SATYA_DEMO_KEYS=1` und einer lokalen Anvil-Chain gedacht. Sie sind **keine** produktiven Identitäten; niemals mit echtem Geld oder auf Celo Mainnet verwenden.

Der Snapshot enthält keine Git-Historie oder Projekt-Remote-Konfiguration und ersetzt kein kanonisches Source-Repository. Die beiden ursprünglichen Ordner `satya-agent/` und `satya/` bleiben getrennte Projektwurzeln. Contract-Abhängigkeiten liegen als Quellkopien vor; ihre ursprünglichen Versions-/Submoduleinträge stehen in `satya-agent/.gitmodules`.

## Letzter bekannter Prüfstand

Im Arbeitsbaum bestanden `npx tsc --noEmit` und `npm run build` (Next.js 15.5.28). `python3 -m py_compile satya/attribution.py satya/x402.py satya/server.py` bestand. Python-`pytest` wurde in dieser Sandbox nicht ausgeführt, weil `pytest` fehlte. Ältere 60/60 Foundry- und 20/20 Python-Ergebnisse beziehen sich auf frühere Projektstände und sind für diesen Snapshot nicht erneut bestätigt.

Insbesondere sind die x402-/ERC-8021-Mainnetpfade nicht produktionsreif. Offene Reviews stehen in [`../../context/current-chat-handoff-2026-11-01.md`](../../context/current-chat-handoff-2026-11-01.md). Kein Mainnet-Payment, Wallet-Signing oder Contract-Deployment wurde durch die Erstellung dieses Snapshots ausgeführt.
