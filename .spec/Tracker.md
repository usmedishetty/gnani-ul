# Implementation Tracker (Tracker.md)
## Project GallaVaani: Milestones, Build Verification & Quality Checklist

---

### 1. Milestone Execution Status

- [x] **M1: Multi-Agent Architecture & Spec-Driven Development (SDD) Suite**
  - [x] Author all 8 foundational specification files inside `.spec/` per SYZYGY framework.
  - [x] Select the single champion tool for all 15 engineering domains.
  - [x] Establish ASD-STE100 technical writing standards and banned marketing vocabulary.
  - [x] Map OpenViking `viking://` memory URI hierarchy.
  - [x] Define PostgreSQL relational schema and Redis TTL structure.

- [ ] **M2: WhatsApp Cloud API Gateway & Burst Coalescer Engine**
  - [ ] Implement FastAPI `/webhook/whatsapp` endpoint with `X-Hub-Signature-256` verification.
  - [ ] Implement Redis `SETNX wamid:{id}` deduplication with $<150\text{ms}$ fast-ack responses.
  - [ ] Build 8-second adaptive debounce window for multi-modal bursts (voice, text, photo chits).
  - [ ] Configure Redis sorted list `inbox:{wa_id}` and unified chronological payload generator.
  - [ ] Integrate Meta Graph API v21.0+ ephemeral media fetch with temporary Bearer tokens.

- [ ] **M3: Gnani AI Speech Engine Pipeline Integration**
  - [ ] Implement `GnaniSTTClient` (REST) and `GnaniSTTStreamClient` (WSS) wrappers for Prisma v3.0.
  - [ ] Configure native OGG/Opus ingestion, `speech_enhancement=True`, and `format="codemix"`.
  - [ ] Implement dynamic 100-SKU `keyterms` injection (colloquial weights and store staples).
  - [ ] Implement `previous_text` lexical priming for merchant voice diffs.
  - [ ] Implement `GnaniTTSClient` SSE wrapper for Timbre v3.0 (`Shivani` / `Avinash` profiles).
  - [ ] Author deterministic Indic text normalizer (expanding numbers, currency, and fractional units).
  - [ ] Build WhatsApp waveform packager uploading to Meta `/media` with `"voice": true`.
  - [ ] Implement Gnani voice cloning (`vachana-vc-v1`) enrollment and parameterized dispatch audio.

- [ ] **M4: Kirana Normalizer, Past Basket Memory & 2-Strike Audio Passthrough**
  - [ ] Build deterministic regex normalizer for colloquial Hindi fractional weights ("pao", "dhai", "sawa").
  - [ ] Implement unit-price and loose-commodity handlers ("10-wali Maggi", "₹20 ki dhaniya").
  - [ ] Build customer basket memory resolver keyed by `wa_id` via `viking://customer/{wa_id}/history`.
  - [ ] Implement FFmpeg word-timestamp audio slicer for low-confidence spans ($<0.68$).
  - [ ] Implement 2-Strike Raw Audio Passthrough logic injecting `VOICE_PASSTHROUGH_SKU`.

- [ ] **M5: Merchant Counter Parchi, 5s Voice Diff & Galla Wake-Up SLA Daemon**
  - [ ] Format `shopkeeper_counter_parchi` interactive slip with 1-tap `[✅ Sab Hai]` action.
  - [ ] Implement merchant swipe-to-reply voice diff parser with cart entity alignment.
  - [ ] Implement 24-Hour Ephemeral Out-of-Stock Cache in Redis with midnight TTL.
  - [ ] Implement Substitution Approval flow for price deltas $>₹15$ or brand replacements.
  - [ ] Build Redis sorted-set SLA monitoring daemon checking order timeouts at 75 seconds.
  - [ ] Integrate automated 10-second outbound IVR ring / missed call via Exotel / soundbox chime.

- [ ] **M6: Four-Rail Bharat Settlement Engine & Raju Dispatch Routing**
  - [ ] Implement Bahi-Khata ledger checking customer limit (default ₹3,000) and generating 2-word tokens.
  - [ ] Implement NPCI-compliant signed dynamic UPI QR generator (`upi://pay?pa=...`) for doorstep card.
  - [ ] Implement Pre-Dispatch UPI Intent lock for new callers with basket values $>₹500$.
  - [ ] Implement Cash-on-Delivery change calculator advisory.
  - [ ] Implement Mohalla-Batched ETA calculator: $T_{\text{pack}}(N) + T_{\text{zone}} + T_{\text{queue}}$.
  - [ ] Build Raju dispatch ticket attaching customer landmark audio and Google Maps pin.

- [ ] **M7: Judge-Proof Twin-Mode Command Center & Pre-Flight Security Gate**
  - [ ] Build Next.js 16 / React 19 split-screen dashboard adhering to OpenDesign `DESIGN.md`.
  - [ ] Implement 1-Click Deterministic Local Webhook Injector with pre-recorded noisy Indian `.ogg` files.
  - [ ] Implement Offline Golden Cache (SHA-256 keyed speech responses) for venue blackout defense.
  - [ ] Execute ASD-STE100 anti-slop validation pass across all interface strings.
  - [ ] Execute Strix multi-agent penetration test against API endpoints and DPDP compliance.

---

### 2. Pre-Flight Verification & Quality Checklist

| Test Suite / Quality Gate | Verification Criteria | Target Result | Tool / Validator |
| :--- | :--- | :--- | :--- |
| **ASD-STE100 Anti-Slop Audit** | Zero banned marketing buzzwords; sentence lengths $<25$ words. | `100% PASS` | `STE100Validator` |
| **Strix Security Scan** | Zero credential leaks, SQL injection vulnerabilities, or insecure endpoints. | `0 Vulnerabilities` | `StrixPentestAgent` |
| **DPDP Act 2023 Compliance** | Welcome consent card verified; STOP command purges customer record. | `VERIFIED` | Unit Test Suite |
| **PII Scrubber Verification** | UPI PINs, OTPs, and card numbers masked as `[REDACTED_SENSITIVE_DIGITS]`. | `100% MASKED` | Regex Test Harness |
| **Prisma v3.0 Ingestion Benchmark**| OGG/Opus transcription turnaround $<450\text{ms}$ with `speech_enhancement=True`. | `PASS` | Benchmarking Suite |
| **Timbre v3.0 Waveform Test** | Synthesized OGG/Opus plays natively in WhatsApp with waveform display. | `VERIFIED` | Meta Graph API Test |
| **75s SLA Escalation Test** | Order in `AWAITING_SHOP_APPROVAL` triggers IVR ring at $75\text{s} \pm 1\text{s}$. | `PASS` | Integration Test |
| **Twin-Mode Replay Verification** | 1-Click injector executes full order lifecycle with Meta Cloud API disconnected. | `100% OFFLINE SAFE`| Live Demo Harness |
