# Satya – Fahrplan bis zur Hackathon-Einreichung

**Stand:** 30. Oktober 2026, 20:24 IST. Dieses Dokument ist eine Planung, keine geprüfte Tatsachensammlung. Fakten stammen aus `conversation-handoff.md` und `module-inventory.md` in diesem Ordner.

**Frist:** Montag, 9. November 2026, 14:30 IST (09:00 GMT). Interne Abgabe: spätestens Sonntag, 8. November, abends.

## Harte Voraussetzungen (laut Handoff)

- Für die Wertung zählt Celo **Mainnet**. Testnet-Transaktionen zählen nicht.
- Agent-Wallet dem Event-Eintrag hinzufügen und deren ERC-8004-Identität vor der Frist aus genau dieser Wallet registrieren.
- Attribution-Tag nachweisen.
- Track-Passung und die Zulässigkeit eines bereits begonnenen Projekts mit dem Veranstalter klären.
- Quellcode muss öffentlich zugänglich sein.

## Offene Lücken laut Handoff

- Kein Mainnet-Deployment, kein Mainnet-Zahlungsfluss.
- Kein öffentliches Quellcode-Repo für die Engine und die Contracts. `manuelpicard/Satya` enthält nur Dokumentation.
- Nullifier ist öffentlich lesbar. Vor Mainnet ist eine Datenschutz- und Linkability-Prüfung nötig.
- `SatyaHumanSBT` hat keine Deploy-Adresse.

## Zeitplan

| Datum | Schritt | Verantwortlich |
| --- | --- | --- |
| Fr 30.10. | Veranstalter fragen: Zulässigkeit, Track | Nutzer |
| Sa 31.10. – So 1.11. | Code bereitstellen (Zip oder öffentliches Repo) | Nutzer |
| Mo 2.11. | Secrets-Scan, Tests soweit möglich, Lückenliste | Claude |
| Di 3.11. | Umfang festlegen: ein Pfad, Ausblick für den Rest | Nutzer, Claude |
| Di 3.11. | Entscheidung über Budget für Mainnet-Transaktion | Nutzer |
| Mi 4.11. – Fr 6.11. | Öffentliches Repo, Attribution-Tag, ERC-8004-Verknüpfung, Datenschutzhinweise | Gemeinsam |
| Fr 6.11. | Einreichungstext und Demo-Skript | Claude (Entwurf), Nutzer (Prüfung) |
| Sa 7.11. | Generalprobe: Demo von Anfang bis Ende | Gemeinsam |
| So 8.11. | Einreichung vorbereiten, Einreichungsformular dry-run | Nutzer |
| Mo 9.11. vor 14:30 IST | Einreichen | Nutzer |

## Entscheidungen, die nur der Nutzer treffen kann

1. Ist das Projekt zulässig, und welcher Track passt?
2. Welcher eine Pfad wird eingereicht?
3. Wird Geld für eine Mainnet-Transaktion freigegeben, und in welcher Höhe?
4. Wird der Quellcode öffentlich gemacht, und welche Dateien genau?

## Realistische Einschätzung

Eine gültige Einreichung ist möglich, wenn Entscheidungen 1 bis 3 bis Dienstag, 3. November, fallen. Ein Sieg ist mit dem bisherigen Stand unwahrscheinlich. Wenn der Veranstalter das Projekt nicht zulässt oder keine Mainnet-Transaktion stattfinden soll, ist keine Wertung möglich.
