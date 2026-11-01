# Arbeitsentwürfe vom 1. November 2026 — nicht freigegeben

Diese Snapshots bewahren die letzten Satya-Codefassungen aus einer nicht versionierten Sandbox-Arbeitskopie, damit eine andere KI oder ein Reviewer sie nachvollziehen kann. Sie sind **kein kanonischer Source-Branch, kein fertiger Patch und keine Produktionsfreigabe**. Vor Übernahme gegen eine frische, gepinnte Projektquelle vergleichen und die offenen Punkte aus [`../../context/current-chat-handoff-2026-11-01.md`](../../context/current-chat-handoff-2026-11-01.md) erledigen.

## Inhalt

- `backend/satya/attribution.py` — experimenteller ERC-8021 Schema-2 Encoder.
- `backend/satya/x402.py` — überarbeiteter x402-/EIP-3009-Entwurf mit Celo-Asset-Metadaten, Relayerpfad und Receipt-/Transferprüfung.
- `backend/satya/server.py` — FastAPI-Angebot und Prüfung vor bezahlter Ergebnisfreigabe.
- `frontend/app/lib/celo.ts` — Celo-Netze, Hash-/Textnormalisierung und Chain-Switch.
- `frontend/app/components/WalletPanel.tsx` — Self-/Wallet-Flow mit Attribution-Sperre.
- `frontend/app/components/X402Panel.tsx` — sichere Quote-/Zahlungsoberfläche, Mainnet standardmäßig aus.
- `frontend/package.json`, `frontend/package-lock.json` — damals getestete Dependency-Dateien.
- `frontend/docs/` — damalige Readiness- und Security-Notizen.

Tests, bekannte offene Risiken, tatsächlicher Buildstatus und die vorgeschlagene Review-Reihenfolge stehen im aktuellen Chat-Handoff. Keine Schlüssel/Seeds/API-Tokens eintragen. Es gab bei der Erstellung dieser Kopie keine Mainnet-Zahlung, Wallet-Signatur oder Contract-Transaktion.
