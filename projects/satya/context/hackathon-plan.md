# Satya — Plan für „Agents on Open Rails“

**Stand:** 31. Oktober 2026
**Frist:** Mo 9. Nov 2026, 09:00 GMT (= 10:00 MEZ = 14:30 IST). Gewinner: 13. Nov.
**Quelle:** https://www.loops.house/agents-on-open-rails (am 31.10. geprüft)

## Entscheidungen (Annahmen, bitte bestätigen)

- Haupttrack: **Build with buy** (1.000 $ auf 5 Projekte; Tag nicht nötig, aber Nachweis bezahlter Dienste).
- Zweiter Eintrag: **USA₮ with x402** (nur wenn echte unabhängige Nutzer gewonnen werden).
- Pitch: nachvollziehbare Herkunft + bezahlbare Prüfung; „unbestimmt“ statt Scheingewissheit. Kein „todsicher“.

## Blocker (Reihenfolge)

1. Quellcode (`satya-agent/`, Python-Paket `satya/`) bereitstellen — liegt nicht in diesem Repo.
2. Falsches „sicheres“ Urteil im Demo-Korpus (1 von 9) analysieren und beheben.
3. Datenschutz: Nullifier in `SatyaCelo` sind on-chain lesbar. Vor Mainnet entscheiden (Hash/Salz, nur SBT, oder bewusst akzeptieren).
4. Regelklärung beim Veranstalter: Projekt vor/nach Kick-off (6. Okt) begonnen?
5. Anmeldung auf der Event-Seite → ERC-8021-Tag erhalten.

## Zeitplan

| Tage | Arbeit |
|---|---|
| 31.10–1.11 | Code übergeben, Urteilsfehler prüfen, Track + Datenschutz festlegen |
| 1.–2.11 | Anmeldung, Tag einbauen, sauberes **öffentliches** Repo (nur Quellcode, keine Demo-Schlüssel, keine Wallet-Archive) |
| 2.–5.11 | Mainnet: Contract, ERC-8004 aus Agent-Wallet, Wallet im Event-Eintrag |
| 3.–6.11 | Agent kauft externe Prüfdienste per x402 ein (verifizierbare Zahlungen) |
| 6.–8.11 | Demo, README, Zahlungsnachweise (Tx-Hashes, Dienste) |
| 8.11 | Einreichen (Puffer bis 9.11, 09:00 GMT) |

## Freigaben nötig (nie automatisch)

Mainnet-Deployments, Signaturen, Zahlungen, ERC-8004-Registrierung, Veröffentlichung eines Repos. Keine Schlüssel in Repos.

## Offene Fragen

- Welche externen Dienste soll der Agent einkaufen (Wasserzeichen-/Forensik-APIs mit x402)?
- Wer sind die unabhängigen Nutzer für den x402-Track?
- Mainnet-Gas (CELO) und USDC/USD₮-Budget vorhanden?
