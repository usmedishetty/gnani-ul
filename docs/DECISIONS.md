# Architecture Decision Records (ADRs) - GallaVaani

> **Project:** GallaVaani (Gnani AI Voice Commerce & Khata Bridge)  
> **Status:** Phase 0 & Phase 1 Approved  
> **Repository:** `gnani-ul`  

---

## ADR-001: Rules-First Kirana Normalizer (Deterministic State Machine)

- **Status:** Accepted
- **Context:**
  The Kirana shopping voice stream contains colloquial Indic vernacular expressions (e.g., *pao*, *aadha*, *sawa*, *dedh*, *dhai*, *sau gram*), price-point packs (*10-wali 4 Maggi*), and past basket references (*wahi pichli baar wali chai*). While LLMs can parse arbitrary natural language, they introduce nondeterministic outputs, hallucinations, token latency (500–1200ms), and per-call operational costs.
- **Decision:**
  Author a pure, deterministic rules-first normalizer in Python (`src/gallavaani/normalizer.py`):
  1. Clause splitting on conversational pauses and conjunctions (`aur`, `aur do`, commas, Devanagari danda).
  2. Multi-tier regex matching for Devanagari numerals (`१, २, ३...`), Indic vernacular fractions, metric units (`kg`, `g`, `l`, `ml`, `packet`, `dabba`), and price-point qualifiers (`₹X-wali`).
  3. Strict past-basket history resolution mapping prior orders to concrete SKUs.
- **Consequences:**
  - Parsing execution completes in < 5ms (0ms network cost).
  - 100% deterministic test coverage with zero risk of phantom items added to customer carts.
  - Satisfies SDD requirement for rules-first architecture before any LLM fallback.

---

## ADR-002: Gnani Indic STT REST v3 vs. WebSocket Streaming

- **Status:** Accepted
- **Context:**
  The user voice notes arrive from WhatsApp as recorded `.ogg` (Opus encoded) voice notes or direct client audio uploads ($\le 10$ seconds). We evaluated whether to maintain persistent WebSocket streaming connections or use the HTTP REST `POST https://api.vachana.ai/stt/v3` endpoint.
- **Decision:**
  Use the HTTP REST endpoint `POST /stt/v3` for Phase 1.
- **Consequences:**
  - Raw WhatsApp `audio/ogg; codecs=opus` audio is accepted natively by the Gnani endpoint without mandatory client-side transcoding.
  - Latency benchmarked at ~2,600ms for 11-second audio clips, easily conforming to the 3,500ms pipeline budget.
  - Significantly reduced operational complexity: no broken socket reconnections or socket heartbeats required in serverless/stateless environments.

---

## ADR-003: Timbre-v3.0 Indic TTS Voice & WhatsApp OGG Transcoding

- **Status:** Accepted
- **Context:**
  The project specification referenced legacy Gnani voices (`Nalini`, `Deepak`). During live API smoke testing, the `timbre-v3.0` model rejected these voices with `HTTP 400: Voice 'Nalini' is not supported by model 'timbre-v3.0'`. Furthermore, WhatsApp requires voice notes to be encoded in 16 kHz or 48 kHz mono OGG/Opus with proper container metadata.
- **Decision:**
  1. Standardize on the official female voice `Shivani` (`model="timbre-v3.0"`, `lang="hi"`).
  2. Implement an automated Indic phonetic number expander (`₹450` $\rightarrow$ *"चार सौ पचास रुपये"*, `#204` $\rightarrow$ *"पर्ची नंबर दो सौ चार"*) to prevent digit truncation or English mispronunciation.
  3. Dynamic FFmpeg pipe transcoding: Ingest the raw 24 kHz WAV returned by Gnani TTS and transcode on the fly to 16 kHz mono OGG/Opus (`libopus`, `-b:a 24k`).
- **Consequences:**
  - High-fidelity natural voice output matching WhatsApp voice message audio player requirements.
  - Redacted live fixtures stored in `tests/fixtures/` ensure deterministic offline testing without burning API credits.

---

## ADR-004: In-Memory FSM & Merchant Diff Engine for Phase 1 MUST Scope

- **Status:** Accepted
- **Context:**
  The SDD specified a full multi-tenant cloud PostgreSQL database with RLS, audit logs, and complex migration rollbacks. However, the approved Phase 0 triage budget allocated 16 hours for the MUST scope, focused on the end-to-end voice cart loop and WhatsApp Parchi readback.
- **Decision:**
  Implement the finite state machine (`OrderStateMachine`) and merchant diff engine (`CartDiffEngine`) in-memory with strict enforcement of Invariants 1–5:
  - *Invariant 1:* Cannot transition to `DISPATCHED` from unverified/unpaid state.
  - *Invariant 2:* Substitutions exceeding price thresholds or brand changes transition immediately to `AWAITING_SUB_APPROVAL`.
  - *Invariant 3:* Stale cart versions reject updates with conflict errors.
  - *Invariant 4:* Merchant out-of-stock (OOS) items are cached ephemerally and suppressed from future cart generations.
  - *Invariant 5:* Dynamic doorstep UPI QR generation (`upi://pay`) with NPCI-compliant signed query params.
- **Consequences:**
  - Enabled rapid, clean Green implementation with 100% test isolation.
  - The FSM and diff interfaces are completely decoupled from persistence, allowing drop-in SQLite/PostgreSQL storage in Phase 2 without modifying pipeline contracts.

---

## ADR-005: Zero-Credit Testing & Live Gateway Partitioning

- **Status:** Accepted
- **Context:**
  Running automated tests in CI or during local development should never consume external API credits or fail due to network hiccups.
- **Decision:**
  Partition test execution:
  - Offline unit, FSM, normalization, diff, and mock pipeline tests run via `pytest -q -m "not live"` using recorded fixtures in `tests/fixtures/`.
  - Live API testing is isolated to `scripts/run_pipeline.py --live` and explicit `@pytest.mark.live` markers executed only during formal manual phase gates.
- **Consequences:**
  - Developers and CI can run `run.bat test` thousands of times with 0 API cost and ~0.8s runtime.
  - Protects the live Gnani API quota while preserving full live end-to-end validation capability.
