# Satya — Mainnet-Recherche für „Agents on Open Rails“

**Stand:** 31. Oktober 2026. Alle Werte stammen aus den Celo-Dokumenten (Quellen unten) und müssen vor jeder Mainnet-Transaktion gegen die Live-Quelle (z. B. Blockscout) geprüft werden. Nichts davon wurde on-chain ausgelöst.

## Adressen Celo Mainnet (Chain ID 42220, CAIP-2 `eip155:42220`)

| Zweck | Adresse |
|---|---|
| ERC-8004 Identity Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| ERC-8004 Reputation Registry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Self SelfAgentRegistry | `0xaC3DF9ABf80d0F5c020C06B04Cced27763355944` |
| Self SelfReputationRegistry | `0x69Da18CF4Ac27121FD99cEB06e38c3DC78F363f4` |
| Self SelfValidationRegistry | `0x71a025e0e338EAbcB45154F8b8CA50b41e7A0577` |
| USDC (x402) | `0xcebA9300f2b948710d2653dD7B07f33A8B32118C` |
| USD₮ (x402) | `0x48065fbBE25f71C9282ddf5e1cD6D6A887483D5e` |
| Permit2 | `0x000000000022D473030F116dDEE9F6B43aC78BA3` |
| USDC-Fee-Currency-Adapter (Gas in USDC) | `0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B` |

Sepolia-Gegenstücke (bereits im Projekt): Identity Registry `0x8004A818BFB912233c491871b3d84c89A494BD9e`, Self Registry `0x043DaCac8b0771DD5b444bCC88f2f8BBDBEdd379`.
`SatyaCelo` muss für Mainnet mit den Mainnet-Adressen neu deployed werden (Konstruktor-/Konfigurationswerte prüfen).

## ERC-8004-Identität

- `register(string agentURI) returns (uint256 agentId)` auf der Identity Registry; mintet ein ERC-721 an die sendende Adresse, **diese Wallet kontrolliert die Identität** — die Wallet verwenden, die der Agent behalten soll und die im Event-Eintrag steht.
- Agent-ID aus dem `Registered`-Event lesen, nicht aus dem simulierten Rückgabewert.
- Registrierungsdatei (JSON, HTTPS/IPFS/`data:`): `type` = `https://eips.ethereum.org/EIPS/eip-8004#registration-v1`, `name`, `description`, `image`, `services[]`, `x402Support`, `active`, `supportedTrust`, später `registrations` (`eip155:42220:<Identity Registry>` + `agentId`). Ablauf: Datei ohne `registrations` hosten → registrieren → ID eintragen → `setAgentURI`.
- Gas in CELO oder per `feeCurrency` in USDC.
- Die bisherige Agent-ID 453 gehört zu Sepolia und zählt nicht.

## Self Agent ID (Mainnet)

- Registrierung braucht auf Mainnet einen **echten Pass/Ausweis**, gescannt in der Self-App; Sepolia akzeptiert Mock-Dokumente. Das kann nur die Person selbst tun.
- Standard-Sybil-Limit: ein Agent pro Mensch. SDK: `@selfxyz/agent-sdk`.

## Attribution-Tag (ERC-8021)

- Paket `@celo/attribution-tags` (+ `viem`): `toDataSuffix(code)` an die Calldata hängen (`concat([callData, tag])`; wagmi: `dataSuffix`).
- Der **zugewiesene Code** (nach Anmeldung) muss exakt verwendet werden; nur der zählt. Format `[a-z0-9_]`, 1–32 Zeichen.
- Prüfen mit `verifyTx({ client, hash })` — nach jeder Tx-Art testen; ERC-4337-Bundler/Relayer können Suffixe entfernen.
- Tag gehört in Frontend/Agent-Backend, nicht in den Contract; keine Plattform-Codes (z. B. `minipay`) selbst setzen.
- **x402:** Der Facilitator schreibt noch keine Tags (Stand der Doku). Für x402-Abwicklungen stattdessen die **PayTo-Wallet** angeben, wie es die Hackathon-Seite verlangt.

## x402 auf Celo

- Facilitator Mainnet: `https://api.x402.celo.org` (Dashboard `https://x402.celo.org`, Config `/api/config`).
- Verkäufer: `@x402/express` (oder `@x402/hono`), `@x402/core`, `@x402/evm`; API-Key im Dashboard per Wallet-Signatur (off-chain) erzeugen, nur auf dem Server als `X402_API_KEY`.
- Auf Celo das explizite `price`-Objekt nutzen (Kurzform `"$0.01"` schlägt fehl). USDC: `extra { name: "USDC", version: "2" }`; USD₮: `{ name: "Tether USD", version: "1" }`.
- Käufer signiert eine Autorisierung und wiederholt die Anfrage mit `PAYMENT-SIGNATURE`; Käufer-Wallet braucht kein CELO (Facilitator zahlt Gas). Ausgabenlimits (`spendControls`) setzen.
- Kosten: Gas + 0,3 % je Abwicklung. **Unklar:** Hackathon-Seite nennt 20 kostenlose Mainnet-Abwicklungen, die Celo-x402-Doku nennt 1 pro Netzwerk — im Dashboard prüfen.

## Konsequenzen für Satya

1. **Build with buy:** Der Agent muss *verifizierte bezahlte Aufrufe* an Dienste senden, die das Team nicht kontrolliert. Bei der Recherche tauchten fast nur andere Hackathon-Projekte als x402-Anbieter auf (z. B. `eddiemessiah/omni402`, „Open Rails Data Agent“). Ob die als „nicht selbst kontrolliert“ zählen und substanziell sind, ist offen; unabhängige, echte Dienste (Wasserzeichen-/Forensik-/Daten-APIs) sind noch zu finden. Erfordert Nachweis: Dienste + Zahlungsbelege (Tx-Hashes). Billige Spam-Aufrufe zählen nichts.
2. **USA₮ with x402:** Satya als Verkäufer braucht *unabhängige* Zahler (Wallet nicht von euch erstellt/zuerst befüllt, mit Celo-Aktivität vor dem Hackathon). Nur realistisch, wenn echte Dritte die Prüfung nutzen.
3. **Datenschutz:** Mit Mainnet-Self-Registrierung und `declareAsHuman` wird ein Nullifier dauerhaft öffentlich und mit der Agent-Wallet verknüpft. Vor dem ersten Mainnet-Deploy entscheiden.
4. **Pass-Scan** und alle Mainnet-Transaktionen/Signaturen/Zahlungen: nur durch die Nutzerin/den Nutzer bzw. nach ausdrücklicher Freigabe.

## Quellen

- Celo ERC-8004: https://docs.celo.org/build/agents/8004
- Celo Self Agent ID: https://docs.celo.org/build-on-celo/build-with-ai/self-agent-id
- Celo x402: https://docs.celo.org/build/agents/x402
- Celo Attribution Tags: https://docs.celo.org/build-on-celo/attribution-tags
- Event-Seite: https://www.loops.house/agents-on-open-rails
