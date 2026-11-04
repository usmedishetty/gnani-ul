# Phase 0 Discovery, Gap Analysis & Triage Report (GallaVaani)

> **Harness Platform:** Google Antigravity (AGY) & Antigravity-ECC  
> **Date:** November 4, 2026 (Phase 0 Milestone)  
> **Challenge:** Great Indian AI Internship Challenge 2026 (Gnani.ai)  
> **Primary Award Categories:** "Real Deal" & "Mixed Vibes"  
> **Time Horizon:** Nov 4 – Nov 7 night (~32–36h per teammate, ~64–72 total person-hours)  

---

## 1. Executive Summary & Diagnostic Verification

Antigravity-ECC diagnostic suite (`$ECC doctor`) executed successfully:
- **Node.js Runtime:** v24.19.0 (Healthy)
- **Agent Definitions:** 78 agents registered across planning, build, review, domain, and security tiers.
- **Skills Catalog:** 334 modular skill packages registered.
- **Command Shims:** 96 slash-command shims available in `.agents/commands/`.
- **Hook Runtime:** 15 hooks active (compaction at 135k tokens, AgentShield secret leak blocker, test re-verification).
- **Harness Status:** `HEALTHY` (Zero blocking failures).

---

## 2. Toolbelt Configuration

In accordance with `AGENTS.md`, `CONSTITUTION.md`, `docs/AGENT-CATALOG.md`, and `.agents/commands/`, the operational toolbelt is populated with exact canonical pairings:

| Stage / Domain | Slash Command | Specialist Agent | Permitted Tools / Skill Package |
|---|---|---|---|
| **Research** | `/research` | `research-first` | `view_file`, `search`, `browser` (`web-research-extraction`) |
| **Tests / Verification** | `/test` | `test-coverage-enforcer` | `view_file`, `run_command` (`jest-unit-patterns` / `pytest`) |
| **TDD (Red-Green-Refactor)**| `/tdd` | `tdd-driver` | `view_file`, `replace_file_content`, `write_file`, `run_command` (`red-green-refactor`) |
| **Backend Implementation** | `/python-fastapi` | `python-backend-engineer` | `view_file`, `replace_file_content`, `write_file`, `run_command` (Python 3.11+, FastAPI) |
| **Code Review** | `/review` | `code-reviewer` | `view_file`, `search` (`code-quality-review`) |
| **Security Audit** | `$ECC scan --strict` | `security-auditor` | `view_file`, `search` (`secret-leak-detection`, `owasp-top-10-audit`) |

---

## 3. Section A: Gap Report (SDD Modules vs Repo State & Missing Essentials)

### 3.1 Existing Repository Assets
- Specifications: Complete 8-file SDD suite in `.spec/` (`AppFlow.md`, `Architecture.md`, `Design.md`, `PRD.md`, `Rules.md`, `Schema.md`, `TechSpec.md`, `Tracker.md`).
- Governance: `AGENTS.md`, `CONSTITUTION.md`, `project.md`, `token-budget.json`, `.ecc-manifest.json`.
- Documentation: `README.md` (overview), `.env.example` (template).
- Harness: `.agents/` symlinked to Antigravity-ECC harness.

### 3.2 Missing Essentials Audit
1. **`.gitignore` (CRITICAL):**
   - *Status:* Missing from repository root.
   - *Violation:* Violates `PROJECT.md` Rule 1: *".gitignore (.env, .agents/, \*.db, audio outputs) before the first commit. Never print or commit keys."*
   - *Impact:* `.agents/` (thousands of files) is currently tracked and staged in Git index!
2. **Execution & Run Scripts:**
   - *Status:* Missing.
   - *Impact:* No `Makefile`, `run.sh`, or `run.ps1` exists to launch `pytest -q -m "not live"` or boot FastAPI.
3. **Application Source Code (`src/` / `app/`):**
   - *Status:* 0% implemented.
   - *Missing:* Webhook gateway, state machine reducer, Indic normalizer, audio slicer, diff engine, Gnani client adapters.
4. **Test Suite & Recorded Fixtures (`tests/`):**
   - *Status:* 0% implemented.
   - *Missing:* No `tests/` directory, no `pytest.ini`, and critically, no recorded offline Gnani speech fixtures (`tests/fixtures/`) to allow Teammate B to develop at zero credit burn.
5. **Presentation & Demo Mode:**
   - *Status:* 0% implemented.
   - *Missing:* No local deterministic webhook replay script, no mock audio clips, no judge dashboard.

### 3.3 SDD Module Implementation Gap Matrix
| SDD Module ID | Module Description | Spec Reference | Repo Status | Gap |
|---|---|---|---|---|
| **MOD-01** | WhatsApp Ingress & Burst Coalescer | `TechSpec.md §3`, `Architecture.md §1` | ❌ Not started | No FastAPI `/webhook/whatsapp`, Redis `wamid` dedupe, or 8s debounce buffer. |
| **MOD-02** | Gnani Speech AI Integration (Prisma + Timbre) | `TechSpec.md §2`, `Tracker.md M3` | ❌ Not started | No `GnaniSTTClient` (REST/WSS) or `GnaniTTSClient` (SSE) client classes. |
| **MOD-03** | Indic Kirana Normalizer & Slot Extractor | `AppFlow.md §1`, `Schema.md §4` | ❌ Not started | No colloquial regex unit normalizer (`pao` $\rightarrow$ 250g, `10-wali`). |
| **MOD-04** | Merchant 5s Voice Diff Engine & FSM | `AppFlow.md §2`, `Rules.md §3` | ❌ Not started | No cart diff engine, `previous_text` priming, or 5 hard invariants enforcement. |
| **MOD-05** | 2-Strike Raw Audio Passthrough Safety Net | `AppFlow.md Cluster 1`, `PRD.md §4` | ❌ Not started | No FFmpeg audio slicer or low-confidence fallback routing. |
| **MOD-06** | Four-Rail Bharat Settlement & QR Engine | `TechSpec.md §4`, `Schema.md §1` | ❌ Not started | No NPCI dynamic UPI QR generator (`qrcode`) or Bahi-Khata ledger model. |
| **MOD-07** | Mohalla Dispatch & 75s SLA Wake-Up | `AppFlow.md Cluster 4`, `TechSpec.md §4` | ❌ Not started | No ETA calculator, Raju ticket formatter, or Redis SLA timer daemon. |
| **MOD-08** | Judge Command Center & Twin-Mode Replay | `Architecture.md §4`, `Design.md §2` | ❌ Not started | No local webhook injector or offline golden cache (SHA-256). |

---

## 4. Section B: Conflicts Between SDD and PROJECT.md Facts

| # | Spec File & Section | Conflicting Statement in SDD | Ground Truth in PROJECT.md | Proposed Architectural Fix |
|---|---|---|---|---|
| **1** | `TechSpec.md §2.1`, `Tracker.md M3`, `README.md §8` | Mentions endpoint `https://api.vachana.ai/v1/stt` and header `GNANI_API_KEY`. | `PROJECT.md` line 26: Endpoint is `https://api.vachana.ai/stt/v3`, multipart, header `X-API-Key-ID`. | Adopt `PROJECT.md` verified endpoint (`POST https://api.vachana.ai/stt/v3`) and header (`X-API-Key-ID`) as ground truth. Abstract behind `GnaniSTTClient`. Document in `docs/API_NOTES.md`. |
| **2** | `TechSpec.md §2.4`, `PRD.md §2`, `.env.example` | Mentions "Gemini 2.5 Flash / Evon v3.3 via vLLM". | `PROJECT.md` line 29: "Evon is open-weight, not on the API platform. Do not plan around it." | Drop all dependencies on Evon. Implement slot extraction with deterministic Python regex first, with Gemini 2.5 Flash as an optional tool-calling backend. |
| **3** | `TechSpec.md §1`, `Schema.md §1` | Mandates PostgreSQL 16.x (`asyncpg`, Postgres-specific ENUMs, `TIMESTAMPTZ`, `JSONB`). | `PROJECT.md` line 10: "Redis + SQLite/PostgreSQL (cart state, `wamid` idempotency, 8s burst coalescer)". | Use SQLAlchemy 2.0 with asynchronous SQLite (`aiosqlite`) for zero-friction local testing and lightweight hackathon runtime, allowing PostgreSQL via `DATABASE_URL` if deployed. |
| **4** | `Architecture.md §1`, `PRD.md §2` | Requires "DeepSeek Harness (`dsh`) at `Desktop\curated-repos\deepseek-harness` with Cordis plugins". | `PROJECT.md` line 14: Platform is Google Antigravity with Antigravity-ECC (`$ECC`). | Build core pipeline using native Python/FastAPI async workers as specified in `README.md` note ("No Proprietary Agent API Required"), managed through Antigravity-ECC. |
| **5** | `Schema.md §3`, `Architecture.md §1` | Mandates OpenViking URI memory store (`viking://customer/...`). | `PROJECT.md` line 41: Uses SQLite `memory.db` and `docs/DECISIONS.md`. | Replace external OpenViking dependencies with local SQLite / Redis models, persisting cross-phase decisions via `$ECC memory store` and `docs/DECISIONS.md`. |
| **6** | `Architecture.md §1`, `AppFlow.md §1`, `TechSpec.md §2.3` | Mandates live Merchant Voice Cloning (`vachana-vc-v1`) for Ramesh Seth. | `PROJECT.md` lines 28, 30: "UNVERIFIED: ... any 'Agent API', exact TTS path and voice list. Store no audio except test fixtures." | Classify Voice Cloning as high risk / CUT. Use Gnani Timbre v3.0 standard profiles (`Shivani`/`Avinash`) for all audio readbacks. |
| **7** | `Architecture.md §1`, `AppFlow.md §3`, `Tracker.md M5` | Requires automated outbound phone call via Exotel IVR on 75s SLA breach. | `PROJECT.md`: No Exotel telephony API keys or accounts exist. | Simulate 75s Galla Wake-Up escalation via counter soundbox audio chime / Web Audio alert on the Judge Console, plus priority WhatsApp alert. |

---

## 5. Section C: Triage Table (MUST / SHOULD / CUT)

**Single End-to-End User Story for MUST Scope:**  
*A household customer sends a noisy code-mixed Hinglish voice note grocery order on WhatsApp -> GallaVaani ingests & debounces burst -> transcribes via Gnani Prisma v3.0 REST with grocery keyterms -> extracts colloquial quantities ("pao", "10-wali") into an Interactive Parchi -> synthesizes a Hindi readback audio slip via Gnani Timbre v3.0 -> Customer taps [✅ Pakka Karo] -> Shopkeeper receives counter Parchi and gives 1-tap approval OR 5s voice diff -> Diff Engine updates invoice enforcing Invariants 1-3 -> Generates doorstep dynamic UPI QR order slip.*

**Budget Cap:** 32–36 hours per teammate across 4 days (Total: 64–72 person-hours).

| Module ID | Module & Deliverable | Priority | Technical Reason & Scope Justification | Est. Hours | Owner |
|---|---|---|---|---|---|
| **M1-CORE** | Project Setup, `.gitignore`, Makefile & Test Runner | **MUST** | Rule 1 compliance, unstage `.agents/`, establish `pytest -q -m "not live"`. | 3h | Pair (A+B) |
| **M2-SPEECH** | Gnani Speech Client (Prisma v3.0 STT REST + Timbre v3.0 TTS + Mock Fixtures) | **MUST** | Required for challenge compliance (Gnani models); offline fixtures enable Teammate B. | 7h | Teammate A |
| **M3-NORM** | Indic Kirana Normalizer & Cart Slot Extractor (Regex + Gemini fallback) | **MUST** | Core "Mixed Vibes" evaluation: parses "pao bhar", "10-wali", loose produce. | 6h | Teammate A |
| **M4-DIFF** | Shopkeeper Voice Diff Engine & FSM (Invariants 1, 2, 3 + Cart Delta) | **MUST** | Core "Real Deal" evaluation: 1-tap approve or 5s voice note diff with cart conditioning. | 7h | Teammate A |
| **M5-INGRESS**| FastAPI Webhook Gateway, Redis `wamid` Dedupe & 8s Burst Coalescer | **MUST** | Ingests WhatsApp webhooks, fast-acks $<150$ms, buffers customer voice/text bursts. | 7h | Teammate B |
| **M6-UI-WA** | WhatsApp Interactive Parchi & Audio Packager (Meta Graph API & local simulator) | **MUST** | Delivers dual-modality "Speak & Show" cards to Customer & Shopkeeper. | 6h | Teammate B |
| **M7-SETTLE** | Dynamic Doorstep UPI QR Generator & Bahi-Khata Ledger Model | **MUST** | Fulfills Indian retail settlement requirement (`upi://pay` dynamic QR). | 5h | Teammate B |
| **M8-DEMO** | Judge-Proof Twin-Mode Console & 1-Click Local Webhook Injector | **MUST** | Guarantees 0%-fail demo on stage without relying on live Meta webhooks / venue Wi-Fi. | 7h | Teammate B |
| **M9-EVAL** | E2E Integration Suite & Golden Test Corpus (50 Hinglish test audio chits) | **MUST** | Verifies accuracy, latency SLAs, and ensures full interview readiness for both humans. | 5h | Teammate A |
| **M-SUBTOTAL**| **Total MUST Scope Person-Hours** | — | **Teammate A: 28h \| Teammate B: 25h \| Shared: 3h (Total: 56h $\le$ 72h max)** | **56h** | **A + B** |
| **S1-SAFETY** | 2-Strike Raw Audio Passthrough with FFmpeg 3s Audio Slicing | **SHOULD** | Zero-drop ASR fallback for dialect/low-confidence items ($<0.68$). | 5h | Teammate A |
| **S2-SLA** | 75s Galla Wake-Up SLA Timer with Soundbox Chime | **SHOULD** | Solves counter notification blindness; triggers audio alert if unread. | 3h | Teammate B |
| **S3-LOGIST**| Mohalla-Batched ETA Route Calculator & Raju Dispatch Ticket | **SHOULD** | Delivery helper card formatting with landmark audio link. | 3h | Teammate B |
| **S4-TOKEN** | 2-Word Regional Khata Handover Token ("Aam-24") | **SHOULD** | Handover verification for store credit orders. | 2h | Teammate B |
| **C1-VOICE** | Merchant Voice Cloning (`vachana-vc-v1`) | **CUT** | Unverified API, credit consumption, high latency and privacy risk. | — | — |
| **C2-TELE** | Exotel Outbound IVR Telephony Integration | **CUT** | No telephony API keys or infrastructure available. | — | — |
| **C3-HARN** | DeepSeek Harness (`dsh`) & Cordis Plugin System | **CUT** | Redundant; Antigravity-ECC + native Python asyncio is cleaner. | — | — |
| **C4-VIKING**| OpenViking External Memory Service | **CUT** | Non-standard external service; SQLite + Redis is 100% sufficient. | — | — |
| **C5-3DUI** | ThreeUI 3D Canvas Visualizations & Physics Engine | **CUT** | Gratuitous visual bloat; dark obsidian HTML/CSS is faster and cleaner. | — | — |
| **C6-STRIX** | Strix Multi-Agent Autonomous Pentest Cluster | **CUT** | Replaced by `$ECC scan --strict` and deterministic unit test guards. | — | — |

---

## 6. Section D: Pipeline Data & Error Interface Contracts (`docs/INTERFACE.md`)

Full Pydantic v2 schemas, type annotations, and error envelopes are codified in [docs/INTERFACE.md](file:///./docs/INTERFACE.md).  
Summary of verified stage-by-stage data contracts:

1. **Audio Ingress $\rightarrow$ STT:**
   - Input: `AudioPayload` (`audio_bytes: bytes`, `mime_type: "audio/ogg; codecs=opus"`, `sample_rate_hz: 16000`, `channels: 1`).
   - Output: `STTResponse` (`transcript: str`, `confidence: float`, `detected_language: str`, `word_timestamps: list[WordTimestamp]`).
   - Errors: `INVALID_AUDIO_FORMAT`, `GNANI_RATE_LIMITED` (429), `GNANI_TIMEOUT`.
2. **STT $\rightarrow$ Kirana Normalization:**
   - Input: Raw transcript + 100-SKU store dictionary + customer basket history.
   - Output: `CartIntentResult` (`items: list[CartItem]`, `indicative_total: Decimal`, `applied_assumptions: list[str]`).
   - Normalization: `"pao bhar"` $\rightarrow$ `0.25 kg`, `"10-wali Maggi x4"` $\rightarrow$ `qty: 4, unit_price: 10`.
3. **Cart $\rightarrow$ Merchant Diff & FSM:**
   - Input: Active cart + shopkeeper 5s voice override transcript conditioned on `previous_text`.
   - Output: `CartDiffResult` (`diffs: list[ItemDiff]`, `net_price_delta: Decimal`, `requires_customer_consent: bool`).
   - Enforcement: Price delta $> ₹15$ or brand swap forces state `AWAITING_SUB_APPROVAL`.
4. **FSM $\rightarrow$ Parchi Presentation & Speech Synthesis:**
   - Output: `ParchiTextPayload` (`body_text: str`, `buttons: list[ParchiButton]`, `spoken_script_hindi: str`).
   - Input to TTS: `TTSRequest` (`normalized_text: str`, `voice_profile: "Shivani" \| "Avinash"`).
   - Output from TTS: `TTSResponse` (`audio_bytes: bytes`, `mime_type: "audio/ogg; codecs=opus"`).

---

## 7. Section E: Named "Red List" of Test Cases (MUST Modules)

Per Article I of the Antigravity Constitution, these tests will be implemented and verified failing (Red phase) *before* writing functional code:

```
tests/
├── test_stt_client.py
│   ├── test_stt_transcribe_codemix_hinglish_audio (Asserts accurate transcription of Hinglish OGG audio)
│   ├── test_stt_rate_limit_429_exponential_backoff (Asserts 429 backoff retry and clean error wrapping)
│   └── test_stt_mock_fixture_fallback_when_offline (Asserts offline fixture loading when live flag omitted)
├── test_kirana_normalizer.py
│   ├── test_normalizer_colloquial_weights_pao_sawa_dhai (Asserts "pao"->0.25kg, "sawa"->1.25kg, "dhai"->2.5kg)
│   ├── test_normalizer_price_point_packs (Asserts "10-wali Maggi x4" parses quantity 4 and price 10)
│   └── test_normalizer_past_basket_resolution (Asserts "pichli baar wali chai" resolves to Tata Agni 250g)
├── test_fsm_invariants.py
│   ├── test_fsm_invariant_1_prevent_unverified_dispatch (Asserts exception if moving to PACKING without merchant approval)
│   ├── test_fsm_invariant_2_silent_upcharge_protection (Asserts delta > ₹15 forces AWAITING_SUB_APPROVAL)
│   └── test_fsm_invariant_3_stale_button_click_rejected (Asserts old cart version clicks return stale warning)
├── test_merchant_diff.py
│   ├── test_diff_engine_item_swap_and_sub_approval (Asserts Aashirvaad->Pillsbury replacement creates valid delta)
│   └── test_diff_engine_ephemeral_oos_cache (Asserts out-of-stock SKU token cached with 24h TTL)
├── test_webhook_ingress.py
│   ├── test_webhook_wamid_deduplication_idempotent (Asserts duplicate wamid returns 200 without reprocessing)
│   └── test_webhook_burst_coalescing_debounce (Asserts 3 rapid webhooks within 8s produce 1 coalesced batch)
├── test_tts_synthesizer.py
│   ├── test_tts_indic_number_expansion (Asserts "₹450" expands to "chaar sau pachaas rupaye")
│   └── test_tts_mock_fixture_waveform_packaging (Asserts output carries valid OGG/Opus header)
├── test_settlement_qr.py
│   └── test_settlement_dynamic_upi_qr_generation (Asserts valid NPCI upi://pay URI and PNG QR generation)
└── test_twin_mode_demo.py
    └── test_twin_mode_deterministic_local_injection (Asserts end-to-end replay from raw audio to confirmed bill)
```

---

## 8. Section F: Top 3 Risks & Fallback Matrix

| # | Specific Risk & Trigger Condition | Severity & Impact | Concrete Architectural Fallback |
|---|---|---|---|
| **1** | **Gnani STT API Quota Exhaustion (429 / 5,000 credit limit)**<br>*Trigger:* Teammate A has 5,000 credits on one key; running automated test suites against live endpoints will drain credits rapidly. | **HIGH (Blocker)**<br>Development halts; live API unavailable during final evaluation. | **Offline Golden Cache & Fixture Mocking:**<br>1. All regular tests execute against recorded fixtures in `tests/fixtures/` using `pytest -q -m "not live"`.<br>2. Live calls (`pytest -m live`) are gated and run manually only at phase completions.<br>3. Teammate B runs 100% offline at zero credit consumption. |
| **2** | **Meta WhatsApp Webhook Latency & Sandbox Tunnel Drop**<br>*Trigger:* Ngrok tunnel URLs reset; Meta Cloud API experiences delivery latency ($>5\text{s}$) or throttling during hackathon stage presentation. | **HIGH (Presentation Failure)**<br>Live demo freezes in front of judges. | **Judge-Proof Twin-Mode Mirror Console:**<br>1. Split-screen command center features a 1-click Deterministic Local Webhook Injector.<br>2. Injects authentic noisy Indian voice notes directly into `/webhook/whatsapp` locally, bypassing Meta Cloud API entirely while executing live Gnani Prisma/Timbre on stage.<br>3. Offline Golden Cache (SHA-256 keyed) provides instant failover in venue Wi-Fi blackouts. |
| **3** | **Noisy Ambient Interference in Kirana Counter Voice Diffs**<br>*Trigger:* High background noise (ceiling fan, traffic, customer banter) causes ASR entity extraction failure on shopkeeper's 5s voice diff. | **MEDIUM (UX Degradation)**<br>Wrong item substituted or order stalled. | **Lexical Priming & 1-Tap Fallback:**<br>1. Active cart items are serialized into Prisma's `previous_text` parameter to condition the acoustic model on exact item vocabulary.<br>2. If diff confidence $<0.70$, system displays 1-tap WhatsApp interactive buttons (`[✅ Pillsbury ₹240] [❌ Out of Stock]`) instead of dropping the order. |

---

## 9. Next Immediate Steps (Pending User Approval)

1. **User Sign-Off:** Review and approve the Triage Table (MUST / SHOULD / CUT).
2. **Immediate Phase 0 Actions Upon Sign-Off:**
   - Author `.gitignore` (unstage `.agents/`, ignore `.env`, `*.db`, audio outputs, cache).
   - Create `Makefile` and `run.ps1` / `run.sh` entry points.
   - Record initial architectural decisions into SQLite via `$ECC memory store` and `docs/DECISIONS.md`.
   - Initialize `tests/fixtures/` and author the named Red test list.

