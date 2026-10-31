# Satya — Entwurf für die Einreichung (Agents on Open Rails)

**Stand:** 31. Oktober 2026. Entwurf, nichts davon ist eingereicht. Text für die Einreichung auf Englisch, weil die Event-Seite englisch ist.

## Wann gilt ein Projekt als „bereit zur Bewertung“?

Das öffentliche Dashboard von Celo ([openrails-dashboard](https://github.com/celo-org/openrails-dashboard)) zählt ein Projekt als „ready to be judged“, wenn es alle drei hat:

1. eine **ERC-8004-Identität** (Mainnet),
2. mindestens eine **Transaktion mit Attribution-Tag** (Mainnet),
3. ein **öffentliches Repo**.

Das ist unsere Mindest-Checkliste, bevor irgendetwas anderes zählt.

## Track-Strategie

- **Build with buy** (Haupteintrag): Satya-Agent kauft externe Prüfsignale per x402 ein und fasst sie zu einem Beleg-basierten Urteil zusammen. Gewertet werden verifizierte bezahlte Aufrufe an Dienste, die uns nicht gehören; billiger Spam zählt nichts. Nachweis: Dienste + Zahlungsbelege.
- **USA₮ with x402** (zweiter Eintrag, nur bei echten unabhängigen Nutzern): Satyas Prüfendpunkt als bezahlter x402-Dienst, Abwicklung mit realen Dritten.
- Offene Lücke: unabhängige, echte x402-Anbieter auf Celo sind schwer zu finden. `omni402` ist ein kleines Open-Source-Gateway (20 Commits, keine Sterne), das beliebige APIs als x402-Endpunkte anbietet; ob es mainnet-live ist, ist unbestätigt. Eine ehrliche Lösung: mindestens einen *tatsächlich fremden* Dienst einkaufen und dessen Eigentümer dokumentieren.

## Entwurf Projektbeschreibung (englisch)

> **Satya — verifiable provenance for digital content on Celo.**
> Satya does not claim to detect AI. It answers a narrower, honest question: *what can be proven about where this content came from?* A verdict is "certain" only when a cryptographic proof was checked (a valid C2PA manifest, a signed attestation bound to the content hash). Otherwise the answer is **undetermined** — missing metadata never proves human authorship.
>
> Our agent sells a per-request verification service over **x402** and, when a single source isn't enough, **buys** additional checks from independent paid services, then combines them in a deterministic, evidence-tiered verdict ("proof" vs. "hint"). Identity runs through an **ERC-8004** agent identity; human attestations use Self proof-of-personhood.
>
> *Limits:* a signed statement shows who made it, not that it is true; a proof-of-personhood does not prove authorship of a given file. We publish our test corpus results, including mistakes.

(Ehrlichkeit vor Effekt: dieser Text darf nur behaupten, was der Code am Einreichungstag wirklich kann — vor dem Absenden gegen den Stand prüfen.)

## Checkliste vor dem Absenden

- [ ] Anmeldung auf der Event-Seite, Attribution-Code erhalten und exakt eingebaut
- [ ] Öffentliches Repo mit Quellcode (keine Schlüssel, keine Wallet-Archive, Lizenz gesetzt)
- [ ] ERC-8004-Registrierung aus der Agent-Wallet; Wallet im Event-Eintrag
- [ ] Mindestens eine getaggte Mainnet-Transaktion (mit `verifyTx` geprüft)
- [ ] Build with buy: Liste der eingekauften Dienste + Tx-Hashes als Beleg
- [ ] x402: PayTo-Wallet angegeben
- [ ] Zulässigkeit „Code während des Hackathons“ beim Veranstalter bestätigt
- [ ] Demo-Fehlerfall (1 falsches „sicheres“ Urteil) analysiert und im README offen benannt
- [ ] Datenschutzentscheidung zu Nullifiern dokumentiert
- [ ] Einreichung bis spätestens 8. Nov. (Frist: 9. Nov., 09:00 GMT = 10:00 MEZ)
