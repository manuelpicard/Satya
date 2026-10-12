# Recherche- und Wiederverwendungsnotizen

**Snapshot:** Fakten und öffentliche Chain-Prüfung aus 02.–03.10.2026. Diese Notiz ist kein Live-Status für spätere Daten. Vor einer neuen Anleitung oder Empfehlung sind die offiziellen Seiten erneut zu prüfen.

## Opera CELO Rewards — historische Regeln (02.10.2026)

Quelle: [Opera-Ankündigung und Anforderungen](https://blogs.opera.com/africa/2026/04/introducing-celo-rewards-in-opera-for-android-opera-mini-and-opera-news/); ergänzend [Teilnahmebedingungen](https://minipay.to/celo-rewards-promotion-terms-and-conditions).

- Auszahlung laut Seite: 0,6148 CELO pro App/Woche, montags; Qualifikation pro App getrennt.
- Teilnahme: Android-Gerät, erwachsen (mindestens 18 Jahre bzw. volle Rechtsfähigkeit), Wohnsitz in einem gelisteten Land, Teilnahme an Opera Rewards Points und Zustimmung zu den Bedingungen.
- Opera Mini: Version 99.2+, Google-Konto während der gesamten Woche angemeldet, Mini Standardbrowser während der ganzen Woche, mindestens 1 Seitenaufruf an jedem aktiven Tag, Aktivität an mindestens 5 von 7 Tagen, MiniPay aktiviert.
- Opera for Android: Version 98.0+, Google-Konto und Standardbrowser die gesamte Qualifikationswoche, mindestens 15 Seitenaufrufe an jedem Tag, alle 7 Tage aktiv.
- Opera News: Version 14.0+, jeden der 7 Tage aktiv und mindestens 8 Artikel täglich anklicken; kein Google-Login/Standardbrowser erforderlich.
- Die Standardbrowserpflicht für Mini und Opera for Android macht parallele Qualifikation dieser beiden Apps auf einem Gerät unpraktisch/unmöglich, da Android nur einen Standardbrowser gleichzeitig setzt. Mini + News wurde als praktikable Kombination abgeleitet.
- Laut damaliger Liste waren 37 Länder eingeschlossen: Nigeria, Südafrika, Indonesien, Indien, Kenia, Ghana, Tansania, Uganda, Kamerun, Malaysia, Philippinen, Simbabwe, Chile, Kolumbien, Peru, Uruguay, Argentinien, Mexiko, Neuseeland, Australien, Vietnam, Thailand, Sambia, Senegal, Ruanda, Niger, Mali, Guinea-Bissau, Guinea, Gabun, Côte d’Ivoire, DR Kongo (Kinshasa), Republik Kongo (Brazzaville), Tschad, Malawi, Burkina Faso, Benin. Deutschland war nicht gelistet.
- Bedingungen können geändert, pausiert oder beendet werden. Bedingungen in Opera/der MiniPay-Website und der offiziellen Opera-Seite vor jeder Qualifikationswoche nachsehen.

## Ertragsgröße — damalige Überschlagsrechnung

- Zwei erfolgreiche App-Qualifikationen: 0,6148 × 2 = 1,2296 CELO pro Woche.
- Vier Wochen: 4,9184 CELO.
- Durchschnittlicher Kalendermonat (52/12 Wochen): ca. 5,3283 CELO, gerundet 5,33; nur bei lückenloser Qualifikation.
- CoinGecko wurde im Gespräch am 02.10.2026 mit CELO ungefähr 0,09–0,10 USD zitiert. Das entsprach etwa 0,06 USD je App/Woche und ca. 0,11–0,12 USD pro Woche für Mini + News. Preis ist volatil und keine Zusage.

## MiniPay-Einrichtung und Sicherheit

Quelle: [MiniPay FAQ](https://minipay.to/faq), [Opera FAQ (2023)](https://blogs.opera.com/africa/2023/09/minipay-frequently-asked-questions/).

- Opera Mini O-Menü → MiniPay → Aktivieren/Starten; laut FAQ Google-Konto für Aktivierung/Backup nötig; danach den In-App-Schritten folgen. UI kann sich ändern.
- Für CELO Rewards kein Geld einzahlen oder Transaktion senden.
- FAQ beschreibt Wallet als selbstverwaltet: Schlüssel werden auf dem Gerät im Android Keystore gespeichert und im eigenen Google-Konto/Drive gesichert.
- Schutz: Gerätesperre und Google-Konto stark absichern, Updates installieren, nur offizielle App nutzen, PIN/OTP/Wiederherstellungsphrase niemals weitergeben, Empfänger und Betrag vor Transaktionen prüfen. Bestätigte Blockchainzahlungen sind nicht rückgängig zu machen.

## Kostenlose Alternativen, geprüft 02.10.2026

- [Celo Sepolia Faucet](https://faucet.celo.org/): Testnet-Token, kein echtes Mainnet-CELO.
- [Self/Google Cloud USA₮ Faucet announcement](https://blog.celo.org/the-first-f-air-drop-is-here-introducing-self-and-google-clouds-usa-mainnet-faucet-a8bc3dbdc82e): verteilt USA₮, nicht CELO; Identitätsprüfung ist Teil des Angebots.
- [Celo Foundation Grants portal](https://celofoundation.submittable.com/) zeigte bei Prüfung keine offenen Calls.
- Hackathons/Bountys können echten Wert auszahlen, erfordern aber Arbeit und Zahlung ist ungewiss. Keine zusätzliche verlässliche, einfache Gratisquelle für Mainnet-CELO wurde in der damaligen Prüfung bestätigt.
- Nie Vorabgebühren oder private Schlüssel/Seed Phrase für einen angeblichen Claim senden. Staking/DeFi sind keine risikofreien Gratisquellen.

## Öffentliche Wallet-Prüfung am 03.10.2026

- Adresse vom Nutzer: `0x107B8eA19996De0CC43A28A7F8ec9a0E529778B4`.
- Celo Mainnet, Chain-ID 42220. Öffentliche RPC-`eth_getBalance`-Abfrage ergab 0 CELO zum Prüfzeitpunkt; Blockscout `/transactions` und `/internal-transactions` zeigten keine native CELO-Transaktion, `/token-transfers` zeigte einen USDT-Eingang, keinen CELO-Eingang.
- Explorer: [Celo Blockscout address](https://celo.blockscout.com/address/0x107B8eA19996De0CC43A28A7F8ec9a0E529778B4).
- Nur öffentliche Chain-Reads; keine Schlüssel, Signaturen oder Transaktionen. Das war ein Zeitpunktssnapshot, keine Garantie für spätere Einzahlungen.

## Vom Nutzer eingereichter Link

- `https://jaypay-pi-vault.lovable.app/pay?to=manualAI` zeigte eine freiwillige Trinkgeldseite über 1 **Testnet Pi** an JayPay, nicht Mainnet-Pi, CELO oder Geld. Keine Wallet wurde verbunden und keine Zahlung ausgeführt.

## Quellenrang und Vorbehalte

Die oben verlinkten Opera-, MiniPay- und Celo-Seiten sind die damaligen Primärquellen. Kurswerte stammen aus CoinGecko und sind zeitabhängig. Explorer/RPC zeigen öffentliche On-Chain-Daten, aber keine In-App-Eligibility oder ausstehende Opera-Zahlungsberechtigung. Bei jeder Wiederverwendung Datum, Landeliste, App-Versionen, Prämienbetrag, Netz und Wallet-Status live prüfen.
