# Technical Specification (TechSpec)
## Project GallaVaani: Runtime Toolchain, Speech AI Engines & Infrastructure Matrix

---

### 1. Runtime Environment & Dependency Matrix

| Runtime / Component | Version / Specification | Architectural Role | Operational Justification |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11.x or 3.12.x | Backend Orchestrator & Multi-Agent Mesh | Native `asyncio` performance, Gnani AI Python SDK compatibility, audio tensor manipulation. |
| **FastAPI** | $\ge 0.111.0$ | High-Throughput Webhook Ingestion Gateway | Delivers synchronous HTTP 200 OK fast-acks to Meta Graph API within $<150\text{ ms}$. |
| **Node.js** | 20.x LTS | Judge Command Center & UI Console | Next.js 16 (App Router) + React 19 server actions for the dual-transport judge dashboard. |
| **PostgreSQL** | 16.x | Primary ACID Persistence Store | Stores orders, order items, customer addresses, Bahi-Khata ledgers, and audit logs. |
| **Redis** | 7.2.x | High-Speed Cache & In-Memory State Broker | Manages 8-second burst coalescing buffers, `wamid` deduplication, and sorted-set SLA timers. |
| **FFmpeg** | 6.1+ | Audio Pipeline & Segmentation Engine | Audio slicing, format probing, OGG/Opus header parsing, and silence splitting. |
| **Package Managers** | `uv` (Python) + `pnpm` (Node.js) | Lockfile-Deterministic Package Resolution | Instant sub-second environment bootstrapping for local and CI/CD pipelines. |

#### Core Python Dependencies (`requirements.txt`)
- `fastapi>=0.111.0` & `uvicorn[standard]>=0.30.0`: Async ASGI web server.
- `httpx[http2]>=0.27.0`: Async HTTP client for Meta Graph API and Gnani AI REST endpoints.
- `redis>=5.0.4`: Async Redis client for state debouncing and pub/sub.
- `asyncpg>=0.29.0` & `sqlalchemy>=2.0.30`: Async PostgreSQL connection pool.
- `pydantic>=2.7.0` & `pydantic-settings>=2.2.0`: Runtime data validation and typing.
- `websockets>=12.0`: WSS streaming support for Gnani STT live channels.
- `qrcode[pil]>=7.4.2`: Dynamic NPCI-compliant UPI QR code generator.
- `pydub>=0.25.1`: Audio segment slicing and word-timestamp extraction.
- `cryptography>=42.0.0`: SHA-256 webhook signature verification and SecretBox HMAC token generation.

---

### 2. Speech & Voice AI Stack (Gnani AI Deep Integration)

GallaVaani implements deep, verified integration with Gnani AI's proprietary speech models:

```
                          ┌────────────────────────────────────────────────────────┐
                          │                 GNANI AI SPEECH SUITE                  │
                          └────────────────────────────────────────────────────────┘
                                      │                                 │
                 ┌────────────────────┴────────────┐       ┌────────────┴───────────────────┐
                 ▼                                 ▼       ▼                                ▼
       Gnani Prisma v3.0 REST             Gnani Prisma v3.0 WSS   Gnani Timbre v3.0 SSE    Gnani Voice Cloning
      (model="prisma-v3.0")               (Low-Latency Stream)    (model="timbre-v3.0")     (vachana-vc-v1)
      - Audio: Native .ogg/.opus          - Token-by-token ASR    - Dual Voice Profiles:    - 20s Shopkeeper Audio
      - Dynamic Keyterms (100 SKUs)       - Real-time VAD           Avinash / Shivani       - Scoped Embeddings
      - previous_text Lexical Priming     - WebSocket Chunking    - Native Indic Normalizer - Dispatch Confirmations
      - Built-in Noise Enhancement                                - WhatsApp "voice": true
```

#### 2.1 Gnani Prisma v3.0 (`model="prisma-v3.0"`)
- **Transport Mechanisms:** Invoked via `GnaniSTTClient` (synchronous REST) for sub-30s WhatsApp voice notes, and `GnaniSTTStreamClient` (WebSocket) for multi-chunk live audio.
- **Native OGG/Opus Ingestion:** WhatsApp Cloud API delivers voice messages as `audio/ogg; codecs=opus`. Prisma v3.0 natively accepts `.ogg`, `.opus`, `.m4a`, and `.wav` binaries without transcode degradation. Voice notes exceeding 30 seconds are split at natural silence intervals using FFmpeg before parallel transcription.
- **Code-Mixed Language Support:** Initialized with `format="codemix"` and `lang_code="indic-auto"` (supporting regional fallback pairs such as `"hi-IN,en-IN"`, `"kn-IN,en-IN"`, `"mr-IN,en-IN"`).
- **Dynamic `keyterms` Injection:** Every ASR request passes an array of up to 100 contextual strings:
  - Colloquial Indian units: `["pao", "adhpao", "sawa kilo", "dedh kilo", "dhai kilo", "khula", "peti"]`.
  - Store-specific SKUs: `["Aashirvaad", "Fortune Sunlite", "Tata Agni", "Kaka Namkeen", "Everest Chhole Masala"]`.
  - Neighborhood landmarks: Local mohalla names and prominent physical markers.
- **`previous_text` Lexical Conditioning:** When processing the merchant's 5-second voice diff, the customer's active cart items are serialized into `previous_text`. This primes the ASR language model with exact SKU terminology, achieving $>93\%$ entity extraction accuracy in noisy environments.
- **Speech Enhancement:** Hardware-accelerated speech enhancement (`speech_enhancement=True`) strips ceiling fan hums, road traffic rumble, and counter chatter.

#### 2.2 Gnani Timbre v3.0 (`model="timbre-v3.0"`)
- **Endpoint:** `POST /api/v1/tts/sse` via `GnaniTTSClient` with server-sent events for streaming synthesis.
- **Voice Personas:** Configured with `Avinash` (neutral, authoritative male) or `Shivani` (warm, conversational female).
- **Deterministic Indic Text Normalization Layer:** Gnani Timbre requires phonetically expanded Indic numbers and units. Before synthesis, raw cart text undergoes deterministic normalization:
  - Currency: `₹450` $\rightarrow$ `"chaar sau pachaas rupaye"`.
  - Fractional weights: `0.25 kg` $\rightarrow$ `"pao bhar"`, `1.5 kg` $\rightarrow$ `"dedh kilo"`, `2.5 kg` $\rightarrow$ `"dhai kilo"`.
  - Order numbers: `#204` $\rightarrow$ `"parchi number do sau chaar"`.
- **WhatsApp Waveform Audio Packaging:** Synthesized PCM audio is encoded as `audio/ogg; codecs=opus` and uploaded to Meta's `/media` endpoint with `"voice": true`, rendering a native playable waveform in WhatsApp.

#### 2.3 Gnani Voice Cloning (`vachana-vc-v1`)
- **Onboarding Enrollment:** Merchant records a 20-second consent script during store setup. The engine extracts a 512-dimensional `speaker_embedding`.
- **Security Scope:** Speaker embeddings are locked inside an isolated vault. Synthesis is restricted to rigid, parameterized dispatch templates (e.g., `"Namaste {customer_name}, aapka order number {order_id} pack ho gaya hai"`). Prompt injection cannot generate arbitrary statements in the merchant's voice.

#### 2.4 External Reasoning & Unit Normalizer Glue
To parse complex cart intent, corrections, and price diffs, Prisma transcripts pass to a structured JSON tool-calling model (Gemini 2.5 Flash / Evon v3.3 / Llama-3.3-70B via vLLM) backed by a deterministic Python regex normalizer.

---

### 3. Messaging & Communications Stack

```
   ┌───────────────────────┐                  ┌────────────────────────┐
   │ Meta Graph API v21.0+ │ ──[HTTP POST]──► │ FastAPI /webhook/wa    │
   └───────────────────────┘                  └────────────────────────┘
               ▲                                           │
               │ (Send Interactive / Media)                ▼
   ┌───────────────────────┐                  ┌────────────────────────┐
   │ Outbound Queue Worker │ ◄─[Redis Stream]─│ Redis wamid Dedupe     │
   └───────────────────────┘                  └────────────────────────┘
```

#### 3.1 Webhook Ingestion & Deduplication
- **Endpoint:** `POST /webhook/whatsapp` verified via HMAC-SHA256 signature header (`X-Hub-Signature-256`).
- **Immediate Fast-Ack:** Incoming requests execute Redis `SETNX wamid:{id} 1 EX 86400`. If the key exists, the duplicate webhook is dropped immediately. The endpoint responds with `HTTP 200 OK` within $<150\text{ ms}$ to eliminate Meta throttling.
- **Payload Extraction:** Event payload is placed onto Redis stream `stream:whatsapp_inbound` for asynchronous worker processing.

#### 3.2 Ephemeral Media Retrieval Pipeline
1. Inbound webhook indicates `message.type == "audio"`.
2. Worker retrieves ephemeral media URL via `GET https://graph.facebook.com/v21.0/{media_id}` with the platform Bearer token.
3. Media binary is downloaded into memory (`BytesIO`) within 5 minutes of issuance.
4. Binary is forwarded directly to `GnaniSTTClient`. Media files on disk are scheduled for hard deletion after 24 hours.

#### 3.3 Customer Service Window (CSW) Management
- Every incoming message from a customer updates `csw_expires_at = now() + 24h` in Redis.
- **Within 24 Hours:** Free-form interactive messages (up to 3 buttons), interactive list pickers, and native voice notes (`voice: true`) are transmitted at zero Meta conversation cost.
- **Outside 24 Hours:** System switches automatically to pre-approved Meta Utility Templates (`galla_order_v1`, `galla_monthly_khata_v1`).

---

### 4. Four-Rail Bharat Settlement Engine

#### 4.1 Bahi-Khata (Store Credit)
- Condition: `customer.khata_enabled == True` AND `current_khata_balance + order_total <= customer.khata_limit` (default ceiling ₹3,000).
- Handover Token: Cryptographic two-word regional token (e.g., `"Aam-24"`, `"Kela-12"`). Delivery helper marks order fulfilled only upon customer confirmation of the token.

#### 4.2 Doorstep Dynamic UPI QR
- URI Formulation: Standard NPCI string:
  ```text
  upi://pay?pa={merchant_vpa}&pn={merchant_name}&tr=GV{order_id}&am={total}&cu=INR&tn=GallaVaani_Order_{order_id}
  ```
- Delivered as a high-contrast PNG image embedded into Raju's WhatsApp card and customer receipt. Settlement is reconciled via payment gateway webhooks or merchant 1-tap soundbox approval.

#### 4.3 Pre-Dispatch UPI Intent
- Mandatory for first-time customers (`trust_tier == "NEW"`) with basket values exceeding ₹500.
- State remains in `DRAFT_COLLECTING` until payment webhook confirms status `PAID`.

#### 4.4 Cash-on-Delivery (COD) Guardrails
- Permitted for orders under ₹1,000. Helper card includes automated change advisory calculation:
  ```python
  tender_notes = [100, 200, 500]
  likely_tender = min([n for n in tender_notes if n >= order_total] or [500])
  change_due = likely_tender - order_total
  ```

---

### 5. Hardware & Compute Tiers (SYZYGY Matrix Alignment)

GallaVaani matches hardware tiers to operational workloads per the SYZYGY specification:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          COMPUTE TIER MATRIX                                │
├──────────────────────────┬──────────────────────┬───────────────────────────┤
│ Tier                     │ Hardware Profile     │ Designated Workload       │
├──────────────────────────┼──────────────────────┼───────────────────────────┤
│ 1. Ultra-Low Edge Tier   │ CPU Only, 512MB RAM  │ Cactus Needle (14MB SLM)  │
│                          │ Raspberry Pi / POS   │ Offline store fallbacks   │
├──────────────────────────┼──────────────────────┼───────────────────────────┤
│ 2. Workstation Tier      │ 8-16 GB RAM, 4+ Cores│ FastAPI, Redis, Postgres  │
│                          │ Standard Cloud VM    │ DeepSeek Harness (dsh)    │
├──────────────────────────┼──────────────────────┼───────────────────────────┤
│ 3. Consumer GPU Tuning   │ 1x GPU, 4-8 GB VRAM  │ Soup Layer-Streaming      │
│                          │ (RTX 3060/4060)      │ 8B model local adaptation │
├──────────────────────────┼──────────────────────┼───────────────────────────┤
│ 4. Enterprise Pentest    │ 32 GB RAM, Docker    │ Strix Multi-Agent Cluster │
│                          │ Linux Host           │ Pre-flight pentest harness│
└──────────────────────────┴──────────────────────┴───────────────────────────┘
```
