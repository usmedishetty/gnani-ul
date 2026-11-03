# Product Requirements Document (PRD)
## Project GallaVaani: WhatsApp-First Asynchronous Voice-Note Commerce & Khata Bridge

---

### 1. Executive Summary & Problem Statement

#### 1.1 Executive Summary
**GallaVaani** is an asynchronous, voice-note-native commerce and digital Khata bridge designed for Tier 2/3 Indian households and neighborhood kirana shopkeepers. It eliminates application-download friction by operating 100% within WhatsApp. Consumers order goods by sending natural, code-mixed vernacular voice notes, casual text corrections, or photographs of handwritten kitchen chits. Kirana shopkeepers process, verify stock, modify items, and dispatch orders using a 1-tap counter slip or a 5-second voice diff reply.

The platform directly bridges the linguistic and technological gap between vernacular-speaking households and busy, non-typing kirana merchants. GallaVaani combines deep Indic speech intelligence (Gnani Prisma v3.0 and Timbre v3.0) with an automated state machine, colloquial Indian weight normalization, a four-rail settlement engine (Bahi-Khata credit, dynamic doorstep UPI QR, pre-dispatch UPI link, and Cash-on-Delivery), and a zero-drop audio passthrough safety net.

#### 1.2 The Problem Space
1. **Consumer Drop-off on Modern Apps:** Rapid grocery delivery applications (Blinkit, Zepto, Instamart) require smartphone app installs, continuous internet connectivity, and catalog navigation. Tier 2 and Tier 3 consumers prefer ordering from trusted local kiranas via WhatsApp or phone calls in their mother tongue (Hindi, Hinglish, Kannada, Marathi, Tamil, Telugu).
2. **Shopkeeper Friction & High Counter Chaos:** Kirana merchants (Seth ji / Dukandar) cannot manage complex catalog software, inventory portals, or Bluetooth POS keyboards while attending to physical walk-in customers. WhatsApp order messages arrive as unstructured voice notes or long text walls, resulting in skipped items, missed orders, and payment disputes.
3. **Notification Blindness:** In noisy retail environments with blaring ceiling fans, traffic, and physical counter chatter, merchant phone notifications go unnoticed, causing long delivery delays and customer frustration.
4. **Credit Reconciliation & Doorstep Logistics:** Informal credit (*Bahi-Khata*) represents 60–70% of neighborhood sales. Paper-based ledger systems lead to reconciliation errors, delayed payments, and unverified handovers by delivery helpers (*Raju*).

---

### 2. Champion Tool Matrix ("1 Tool for 1 Task" SYZYGY Policy)

Per the **SYZYGY** autonomous multi-agent engineering meta-framework, GallaVaani strictly enforces the single best benchmarked tool for each technical and operational domain:

| # | Task / Engineering Domain | Selected #1 Champion Tool | Primary Source / Path | Architectural Role & Selection Justification |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Multi-Agent Orchestrator** | **DeepSeek Harness (`dsh`)** | `Desktop\curated-repos\deepseek-harness` | Cordis plugin system, 53 built-in tools, headless pipelines, and local web UI (`localhost:3080`). Manages multi-agent execution graphs without framework bloat. |
| **2** | **Agent Workflow Patterns** | **66 Agentic Design Patterns** | `Desktop\curated-repos\Agentic-Design-Patterns` | Antonio Gulli's industry reference: Lead Coordinator (Pattern #7), Dynamic Model Router (Pattern #2), Parallel Subagents (Pattern #3), and Reflection & Self-Correction (Pattern #4). |
| **3** | **Indic Speech-to-Text (ASR)** | **Gnani Prisma v3.0** | `GnaniSTTClient` / `GnaniSTTStreamClient` | Native `.ogg`/`.opus` decoding, code-mixed Indic transcription (`format="codemix"`), `speech_enhancement=True`, store SKU `keyterms` injection, and `previous_text` conditioning. |
| **4** | **Indic Text-to-Speech (TTS)** | **Gnani Timbre v3.0** | `GnaniTTSClient` / SSE (`/api/v1/tts/sse`) | Expressive Hindi/Regional synthesis (Shivani/Avinash), native WhatsApp waveform packaging (`"voice": true`), sub-500ms streaming generation. |
| **5** | **Merchant Voice Cloning** | **Gnani Voice Cloning (`vachana-vc-v1`)** | Speaker Embedding Engine | Captures 20-second merchant onboarding voice sample; generates trust-building personalized WhatsApp audio dispatch cards. |
| **6** | **Research & Paper Extraction** | **Firecrawl Research Index** | `mendableai/firecrawl` | Index of 43M+ scientific papers (arXiv, PubMed); extracts peer-reviewed ASR denoising formulas, Indic acoustic models, and acoustic beamforming research. |
| **7** | **Visual Architecture & Flowcharts**| **Diagram Design + ByteByteGo** | `diagram-design` + `ByteByteGo` | High-fidelity distributed system topology, event-driven state machines, and sequence diagrams. |
| **8** | **UI Design & Judge Console** | **OpenDesign + awesome-design-md** | `nexu-io/open-design` | Dark obsidian (`#090D16`) split-screen command console powered by `DESIGN.md` contracts and spring physics. |
| **9** | **Frontend 3D & Motion Physics**| **ThreeUI + Motion Engine** | `threeui` + `motion` | Hardware-accelerated transitions and telemetry charts on the live presentation console. |
| **10**| **Context DB & Agent Memory** | **OpenViking (`viking://`) + AgentMemory** | `OpenViking` + `agentmemory` | Cross-session memory for customer basket history, merchant daily OOS cache, and multi-agent coordination states. |
| **11**| **Autonomous Security Pentesting** | **Strix Multi-Agent Pentesting** | `Desktop\curated-repos\strix` | Scans API endpoints, tests DPDP Act 2023 compliance, inspects WhatsApp webhook signatures, and audits PII scrubbing. |
| **12**| **Anti-AI Slop & Documentation** | **Simplified Technical English (ASD-STE100)**| `simplified-technical-english` | Strict aerospace writing standard: sentences under 25 words, zero marketing buzzwords, unambiguous imperative directives. |
| **13**| **AI Presentation / Pitch Deck** | **PPT Master** | `repos\ppt-master` | Generates native vector PowerPoint shapes and text frames adhering to the SIH Grand Finale 10-slide standard. |
| **14**| **On-Device Edge Model** | **Cactus Needle** | `repos\needle` | 14MB model running in 28MB RAM; executes command tool-calling locally for offline edge fallbacks. |
| **15**| **Consumer GPU Fine-Tuning** | **Soup** | `repos\Soup` | Layer-streaming fine-tuning of 8B models on 4GB VRAM for hyper-local store SKU vocabulary adaptation. |

---

### 3. Target Personas & User Profiles

#### Persona 1: Sunita Ji (Tier 2/3 Household Consumer)
- **Profile:** 42-year-old homemaker in Awas Vikas, Kanpur. Uses WhatsApp exclusively for family groups and video calls. Low typing speed, zero English app literacy.
- **Behavior:** Orders groceries 3–4 times per week. Holds the WhatsApp microphone button to record unstructured Hinglish voice notes containing local measurements ("pao bhar hari mirch", "10-wali Maggi", "wahi pichli baar wali chai").
- **Payment Method:** Prefers neighborhood Bahi-Khata credit or doorstep PhonePe/GooglePay QR scanning upon delivery.
- **Pain Points:** Confused by catalog-heavy e-commerce apps; cannot search for regional ingredients; fears typing wrong quantities.

#### Persona 2: Ramesh Seth (Kirana Store Owner / Dukandar)
- **Profile:** 48-year-old proprietor of Sharma Provision Store. Manages 400+ daily counter transactions alongside inventory and wholesale deliveries.
- **Behavior:** Keeps phone on the glass counter next to the cash drawer (*galla*). High background ambient noise (ceiling fan, street traffic, customer banter). Rejects any system requiring typing or manual catalog entry.
- **Interaction Style:** Needs a 1-tap confirmation button (`[✅ Sab Hai - Pack Karo]`) or a 5-second voice override when stock is missing ("Aashirvaad khatam hai, Pillsbury rakh diya ₹240 ka").
- **Pain Points:** Misses WhatsApp order notifications during peak counter rush; cannot update item prices; loses track of informal customer credit balances.

#### Persona 3: Raju (Mohalla Delivery Helper)
- **Profile:** 20-year-old store delivery assistant. Operates a budget Android smartphone on 4G.
- **Behavior:** Delivers 25–40 orders daily across narrow mohalla alleys without structured street addresses or postal codes.
- **Interaction Style:** Receives a structured WhatsApp dispatch card containing order items, cash/UPI collection amount, dynamic QR code, and a playable 5-second customer landmark audio note.
- **Pain Points:** Gets lost in unmapped alleys; cannot locate house numbers; carries incorrect change for cash orders; experiences customer disputes on delivered item counts.

---

### 4. The 9 Concrete Functional Improvements

#### Improvement 1 — Multi-Modal "Burst Coalescing" Customer Intake
Customers frequently send an 18-second voice note, immediately follow it with a 2-second text correction ("mirch pao nahi aadha kilo"), and upload a photograph of a handwritten kitchen chit. GallaVaani initiates an 8-second adaptive debounce window in Redis (resetting on incoming typing indicators, audio uploads, or rapid webhooks). The intake pipeline coalesces all inputs into a single unified Provisional Parchi instead of firing fragmented, conflicting confirmations.

#### Improvement 2 — Dual-Modality "Speak & Show" Reply Cards
Every order confirmation sent to the customer consists of two synchronized WhatsApp payloads:
1. An Interactive Button Message ([✅ Order Pakka Karo], [🎙️ Badlo / Jodo], [💳 Payment/Pata]) in English + Regional script (Hindi/Devanagari).
2. A 6-second native WhatsApp Voice Note (`Timbre v3.0`, encoded as `audio/ogg; codecs=opus`, payload attribute `"voice": true`) reading back the line item count, total indicative bill, and applied assumptions.

#### Improvement 3 — The Shopkeeper's "Zero-Typing Parchi" (1-Tap Approve OR 5-Second Voice Diff)
The merchant receives a compact counter slip on WhatsApp formatted like a traditional Indian invoice:
- **Happy Path (80% of orders):** Shopkeeper taps `[✅ Sab Hai - ₹435 Pack Karo]`. Execution time: 1.5 seconds.
- **Exception Path (20% of orders):** Shopkeeper swipes to reply on the WhatsApp slip and records a 5-second voice note ("5 kilo wala Aashirvaad khatam hai, 1-1 kilo ke 5 packet rakh diye hain, aur dhaniya free dal diya"). Prisma v3.0 (primed with current cart items in `previous_text`) transcribes the audio, and the Diff Engine updates the order state without manual data entry.

#### Improvement 4 — The "2-Strike Raw Audio Passthrough" (Zero-Drop ASR Safety Net)
When a customer voice note contains an obscure regional brand, hyper-local masala, or dialect-heavy SKU where Prisma v3.0 confidence or fuzzy matching falls below 0.68 after one clarification attempt, GallaVaani never triggers a third prompt. It uses word-level timestamps to crop the exact 3-second audio segment via `ffmpeg`, injects `[🎵 Voice Item #4 (Listen)]` into the cart, and forwards the cropped audio snippet directly to the shopkeeper's slip for human pricing and fulfillment.

#### Improvement 5 — Four-Rail Bharat Settlement Engine
Accommodates all Indian retail payment paradigms:
1. **Bahi-Khata (Digital Store Credit):** Enabled for whitelisted phone numbers under merchant-set credit limits (default ₹3,000). Generates a 2-word regional delivery token (e.g., "Aam-24") for verification at handover.
2. **Doorstep Dynamic UPI QR:** Injects an NPCI-compliant signed `upi://pay` URI rendered as a high-contrast QR image inside Raju's WhatsApp card.
3. **Pre-Dispatch UPI Intent Link:** Enforced for first-time callers or baskets exceeding ₹500. Order packing begins only after payment webhook confirmation.
4. **Capped Cash-on-Delivery (COD):** Displays exact cash tender advisories to Raju (e.g., "Customer will give ₹500 note — carry ₹135 change").

#### Improvement 6 — Hybrid "Pin + Landmark Voice Clip" Address Vault
- **Repeat Customers:** Automatically keyed by WhatsApp `wa_id`; previous delivery address and mohalla landmark are pre-filled on the provisional card.
- **First-Time Customers:** Bot prompts for WhatsApp Location Pin (`location_request_message`) plus a 5-second spoken landmark voice note ("Pani ki tanki ke peeche, hara gate").
- Both the Google Maps deep-link and the raw 5-second customer landmark audio note are forwarded to Raju's dispatch card.

#### Improvement 7 — Queue-Aware & Mohalla-Batched ETA Calculator
Calculates accurate delivery ETAs using:
$$\text{ETA (minutes)} = \lceil T_{\text{pack}}(N_{\text{items}}) + T_{\text{zone}}(\text{Mohalla}) + \max(0, T_{\text{helper\_busy\_remaining}} - T_{\text{pack}}) \rceil$$
Automatically detects orders within the same mohalla radius placed within 12 minutes and injects `[⚡ BATCH WITH ORDER #104 - SHASTRI NAGAR]` onto the merchant's slip.

#### Improvement 8 — 75-Second "Galla Wake-Up" Escalation Protocol
Overcomes ambient noise and WhatsApp notification blindness at busy retail counters. If a confirmed customer order remains unread or unacknowledged on the shopkeeper's phone for 75 seconds, GallaVaani initiates an automated 10-second outbound IVR ring / missed-call trigger (or secondary counter soundbox chime) to capture merchant attention.

#### Improvement 9 — Judge-Proof "Twin-Mode" Demo Architecture
Prevents live hackathon stage failures caused by conference Wi-Fi bottlenecks, Meta sandbox rate limits, or cellular dead zones. The dual-transport Judge Command Center features:
1. Live WhatsApp Cloud API mode.
2. 1-Click Deterministic Local Webhook Injector with pre-recorded noisy Indian voice notes.
3. Offline Golden Cache for instant, local failover.

---

### 5. Quantified Success Metrics & Target SLAs

| Metric Category | Target SLA / Threshold | Measurement Methodology |
| :--- | :--- | :--- |
| **ASR SKU & Unit Extraction Recall** | **$\ge 93.0\%$** on noisy code-mixed audio | Benchmarked against 50 Hinglish/Kanlish audio samples with Prisma v3.0 `keyterms` enabled vs. baseline. |
| **End-to-End Turnaround Latency** | **$< 2.8\text{ seconds}$ (P95)** | Timed from Meta webhook reception to outbound WhatsApp readback transmission. |
| **Merchant Happy-Path Action Time** | **$< 2.0\text{ seconds}$** | Time delta between merchant counter slip delivery and `[✅ Sab Hai]` tap webhook. |
| **Merchant Voice Diff Action Time** | **$< 7.0\text{ seconds}$** | Time delta from merchant swipe-to-reply voice note submission to updated customer card. |
| **Zero-Drop Order Completion Rate** | **$\ge 99.2\%$** | Ratio of initiated customer voice baskets reaching `CONFIRMED_PACKING` without bot loops. |
| **Total AI & Messaging Cost per Order** | **$< ₹0.85 / \text{order}$** | Free-form messages within 24h Customer Service Window + sub-30s Gnani speech calls. |
| **Galla Wake-Up Dispatch Accuracy** | **$100\%$ within $75\text{s} \pm 2\text{s}$** | Monitored via Redis sorted-set SLA timers. |

---

### 6. MVP Scope & Explicit Non-Goals

#### In-Scope for Challenge MVP (Mandatory Deliverables)
1. **WhatsApp-First Customer Interface:** Natural Hinglish voice note ingestion, burst coalescing, dual-modality Interactive Parchi, and Timbre v3.0 voice notes.
2. **Kirana Normalization & 2-Strike Audio Passthrough:** Colloquial weight parsing ("pao", "adh-pao", "sawa"), historical basket resolution, and raw audio slicing for low-confidence items.
3. **Shopkeeper WhatsApp Loop:** 1-tap button confirmation, 5-second swipe-to-reply voice diff with `previous_text` lexical priming, and 75s Galla Wake-Up escalation.
4. **Four-Rail Bharat Settlement & Raju Ticket:** Digital Khata token, dynamic doorstep UPI QR generation, pre-pay link, and delivery helper WhatsApp ticket with landmark audio.
5. **Judge Command Center with Twin-Mode Replay:** Real-time 3-pane split-screen console, live state machine inspector, Gnani telemetry logs, and 1-click deterministic local webhook injector.

#### Explicit Non-Goals (Strictly Excluded)
1. **No Native Mobile Apps:** Neither customers, merchants, nor delivery assistants download any iOS/Android app. All interactions occur via WhatsApp and the web-based Judge Console.
2. **No Full ERP / Warehouse Inventory Engine:** Shopkeepers do not conduct wholesale catalog data entry or barcode scanning. Availability is resolved lazily per order and stored in the 24-hour Ephemeral Out-of-Stock Cache.
3. **No Continuous GPS Telemetry Polling:** No real-time driver tracking maps or live geolocation streams. Dispatches use mohalla-ring ETA formulas and milestone status updates.
4. **No Direct Card / PCI-DSS Vaulting:** Payment processing strictly leverages NPCI `upi://pay` standard intents, dynamic QR codes, soundbox triggers, and merchant Bahi-Khata ledgers.
5. **No Multi-Seller Marketplace Aggregator:** GallaVaani empowers direct 1-to-1 relationships between local households and their neighborhood kirana.
