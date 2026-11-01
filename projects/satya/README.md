# Satya — privates Projekt-, Quellcode- und Gesprächsarchiv

Dieses Verzeichnis bewahrt den für zukünftige KI-Sitzungen aufbereiteten Satya-Projektkontext **und den aktuellen vollständigen Quellcode-Snapshot**. Das Repository ist **privat** und darf nicht öffentlich gespiegelt werden.

## Schnellstart für eine neue KI

1. Zuerst [`context/current-chat-handoff-2026-11-01.md`](context/current-chat-handoff-2026-11-01.md) lesen.
2. Vollständiger Code: [`source/2026-11-01/`](source/2026-11-01/README.md). Darin liegen beide Wurzeln `satya-agent/` (Frontend, Solidity) und `satya/` (Python-Engine/API).
3. Vor produktiver Übernahme die offenen Punkte und Testgrenzen im Handoff beachten. Der Source-Snapshot ist eine datierte Kopie ohne Git-Historie; er ist kein Beleg für Security-Audit, Deployment oder Hackathon-Einreichung.

## Weitere Projektunterlagen

- [`context/conversation-handoff.md`](context/conversation-handoff.md) — frühere kuratierte Projekterinnerung.
- [`context/module-inventory.md`](context/module-inventory.md) — Modulkarte für Python-Engine/API, Next.js-dApp, Solidity-Verträge, Tests und Demo.
- [`context/hackathon-plan.md`](context/hackathon-plan.md), [`context/mainnet-research.md`](context/mainnet-research.md), [`context/submission-draft.md`](context/submission-draft.md) — Hackathon-Planung, Recherche und Einreichungsentwurf.
- [`work-in-progress/2026-11-01/`](work-in-progress/2026-11-01/README.md) — isolierte Einzeldatei-Snapshots der jüngsten x402-/Attribution-Änderungen; zur schnellen Review, nicht anstelle des vollständigen Source-Baums.

## Datenschutz und Sicherheit

Das Handoff ist eine kuratierte Erinnerung, kein wortgetreues Gesprächstranskript. Der Source-Snapshot lässt lokale `.env`-Dateien, Python-/Foundry-/Next-Buildartefakte und `*.key`-Dateien weg. `server.py` enthält feststehende lokale Anvil-Demo-Keys, die ausschließlich für eine lokale Testchain vorgesehen sind; niemals auf Mainnet verwenden. Keine echten privaten Schlüssel, Seeds, Zugangsdaten oder API-Tokens hinzufügen. Keine Wallet-Signatur, Mainnet-Transaktion, Zahlung, Registrierung oder öffentliche Veröffentlichung ohne separate Nutzerfreigabe.
