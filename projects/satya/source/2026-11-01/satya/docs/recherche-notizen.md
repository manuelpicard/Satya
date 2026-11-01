# Satya – Recherche-Notizen (Stand 2026-10-02)

## Projektkontext
- Projekt "satya", Projektanweisung: "Layer 2". Layer 1 = HMN Human Credential (/home/ubuntu/human-token). Satya = Layer 2 (Inhalts-Herkunft).

## EU AI Act Art. 50
- EU-Kommission FAQ (Stand 24.07.2026): https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act
  - Art. 50 gilt ab 2. Aug 2026. Art. 50(2): Anbieter generativer KI müssen Ausgaben maschinenlesbar markieren, "effective, reliable, robust and interoperable", erkennbar als KI-generiert/manipuliert.
  - Übergangsfrist nur für vor 2.8.2026 in Verkehr gebrachte Systeme, nur für Art. 50(2): bis 2. Dez 2026.
  - Ausnahmen: kurze Zeichenfolgen, Quellcode, Maschine-zu-Maschine, assistive Standardbearbeitung.
  - Art. 50(4): Deployer müssen Deepfakes und KI-Texte zu Themen öffentlichen Interesses kennzeichnen (außer mit menschlicher Prüfung/redaktioneller Kontrolle).
  - Bußgelder bis 15 Mio. EUR oder 3 % Jahresumsatz.
  - Code of Practice on Transparency of AI-generated content: final veröffentlicht 10. Juni 2026 (casrai), von Kommission und AI Board als angemessen bewertet.
- MoFo (11.09.2026): https://www.mofo.com/resources/insights/260911-full-transparency-organizations-sign-eu-code
  - ~190 Organisationen bis Ende Juli unterzeichnet; Stand 9.9.2026: 82 Provider, 152 Deployer.
  - Provider müssen kostenlose Erkennungstools anbieten und Manipulation in AGB verbieten.
  - Google: SynthID + C2PA. Anthropic (14.08.2026): künftige Claude-Modelle erzeugen Text mit Wasserzeichen (Variante von SynthID-Text), Detection-API geplant; C2PA-Metadaten für Dateien.
  - OpenAI: C2PA + SynthID für Bilder, seit 31.07.2026 auch Audio; arbeitet an Text.
  - Synthesia: C2PA für Videos.

## OpenAI Provenance
- https://openai.com/index/advancing-content-provenance/ (19.05.2026, Update 31.07.2026)
  - OpenAI ist C2PA Conforming Generator Product; SynthID-Wasserzeichen in Bildern von ChatGPT, Codex, API (Partnerschaft Google). Öffentliches Verifikationstool (nur OpenAI-Inhalte); API-Zugang für Verifikation.
  - Zitat: "No detection method is foolproof ... If no metadata or watermark is detected ... the tool will not make a definitive conclusion".
  - Metadaten können abgestreift werden (Upload, Screenshot, Formatwandlung).

## C2PA
- casrai Guide (verifiziert 25.09.2026): https://casrai.org/guides/c2pa-content-credentials-explained
  - Spezifikation 2.2 (Mai 2025), 2.4 (April 2026). ISO/DIS 22144 (Entwurf).
  - Validierungsstufen: well-formed / valid / trusted. Trust List + Conformance Program seit Mitte 2025; Interim Trust List seit 1.1.2026 eingefroren.
  - Hard binding (Hash, bricht bei Re-Encoding) vs. soft binding (Wasserzeichen/Fingerprint, schwächer).
  - Zitat Spezifikation: provenance "cannot tell you whether the digital content is true".
  - "a detector that is wrong produces a confident false accusation, whereas a provenance chain that is broken produces an absence of information. Absence of a credential is not evidence of manipulation"
- Golaszewski et al., arXiv:2604.24890 (23.04.2026) "Verifying Provenance of Digital Media: Why the C2PA Specifications Fall Short": formale Analyse; ungeschützte Zeitstempel, optionale Revocation, inkonsistente Validatoren; "should not yet be relied upon for high-stakes uses such as financial disclosures, journalism, or legal evidence."
- Trust List: https://github.com/c2pa-org/conformance-public/tree/main/trust-list (C2PA-TRUST-LIST.pem: 30 Zertifikate; TSA: 22) – heruntergeladen am 02.10.2026.
- Pixel 10: C2PA in jedem Foto standardmäßig (Google Security Blog 10.09.2025): https://security.googleblog.com/2025/09/pixel-android-trusted-images-c2pa-content-credentials.html

## Eigener Test (02.10.2026)
- Bild via gpt-image-2.5 erzeugt: C2PA-Manifest, Signierer "OpenAI OpCo, LLC" / "OpenAI Media Service", digitalSourceType trainedAlgorithmicMedia, Aktion c2pa.watermarked.unbound; mit offizieller Trust List: Trusted (timeStamp.untrusted info).
- Bild via nano-banana-2 erzeugt: Signierer "Google LLC" / "Google Media Processing Services", trainedAlgorithmicMedia, "Applied imperceptible SynthID watermark"; Trusted; zusätzlich XMP/IPTC-Metadaten in PNG.

## Grenzen der Erkennung (Forschung)
- Sadasivan et al. 2023, "Can AI-Generated Text be Reliably Detected?" arXiv:2303.11156 – Paraphrasierung bricht Detektoren; theoretische Grenze (Total Variation), je näher KI an menschlicher Verteilung, desto schlechter.
- Zhang et al. 2023, "Watermarks in the Sand: Impossibility of Strong Watermarking for Generative Models" arXiv:2311.04378 – starkes Watermarking unter natürlichen Annahmen unmöglich.
- Liang et al. 2023, "GPT detectors are biased against non-native English writers", Patterns, arXiv:2304.02819.
- arXiv:2607.16010 (17.07.2026) "AI Watermark Evidence Fails Forensic Readiness": KGW, Unigram, SynthID-Text (MarkLLM-Implementierung); nach Paraphrase 100 % / 100 % / 98,3 % Entfernung; False-Negative vor Angriff 70/83/80 %; SynthID flaggte 5,4 % paraphrasierter menschlicher Kontrolltexte; erfüllt max. 2 von 5 Daubert-Faktoren.
- OpenAI AI Text Classifier eingestellt Juli 2023 wegen geringer Genauigkeit (bekannt).
- Krishna et al. 2023 "Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense" (NeurIPS 2023) – Retrieval-basierte Erkennung durch Anbieter.

## Tools
- c2pa-python 0.38.0 (SDK c2pa-rs 0.91.0), invisible-watermark 0.2.0, web3 8.0.0, eth-account 0.14.0.

## Arbeitsstand (17:04)
- Contracts: /home/ubuntu/satya/contracts (SatyaRegistry.sol, 17/17 Foundry-Tests grün). Gas: attest ~137k, anchorSeal ~148k, attestAI ~99k.
- Python-Paket satya/: model, verdict, hashing, c2pa_check, metadata_check, watermark_check, seal, ledger, engine, cli, server. pytest: 20/20 grün (inkl. hypothesis-Eigenschaftstests).
- Demo: demo/make_demo_ca.py, c2pa_sign.py, seed_chain.py (Anvil :8545, deployment.json: hmn 0x5FbDB2315678afecb367f032d93F642f64180aa3, registry 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512), generate_ai_texts.py (gpt-5-mini), build_corpus.py (22 Fälle), evaluate.py -> demo/auswertung.json.
- Auswertung Phase 1: 22 Fälle, 9 sicher (8 korrekt, 1 falsch = #22 Mallory-Lüge), Abdeckung 40,9 %; naiver Indizien-Detektor: 16 Antworten, 5 falsch, davon 3 falsche KI-Beschuldigungen (#08 gefälschte Signatur, #09 SD-Wasserzeichen, #10 SD-Parameter), #19 KI-Agent-Siegel -> naiv „Mensch“, #22.
- Phase 2 (Betrug aufgedeckt: flagFraud + HMN-Revoke fraud=true): 9 sicher, 0 falsch; #20 WIDERSPRUCH -> KI_NACHGEWIESEN; #22 -> UNBESTIMMT.
- Offenes SD-Wasserzeichen (invisible-watermark 0.2.0 dwtDct, numpy 2.5.3, opencv 5.0.0): Einbettung nur in 3/25 Bildern wieder auslesbar (≥95 % Bits), 0/25 Fehlalarme; Decoder liefert auf sauberen Bildern fast nur 1en oder 0en (Nullmodell verletzt).
- Webserver: uvicorn :8000, öffentlich https://8000-ik0hj4pg1fxauwdkyapdp-ca9f6603.sg2.manus.computer/ (ENV SATYA_RPC, SATYA_REGISTRY, SATYA_DEMO_CA, SATYA_DEMO_KEYS=1).
- Noch offen: UI-Sichtprüfung, Konzeptdokument (docs/Satya-Konzept.md + PDF + Diagramm), README, docs/auswertung.md, ZIP.
