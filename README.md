# GallaVaani (WhatsApp-First Edition)
> **An Asynchronous, Voice-Note-Native Commerce & Khata Bridge for Bharat**  
> *Built with Gnani AI Speech Models & Spec-Driven Development (SDD) via SYZYGY*

[![Meta WhatsApp Cloud API](https://img.shields.io/badge/Meta%20Cloud%20API-v21.0%2B-25D366?logo=whatsapp&logoColor=white)](https://developers.facebook.com/docs/whatsapp/cloud-api)
[![Gnani AI Prisma](https://img.shields.io/badge/Gnani%20Prisma-v3.0%20ASR-6366F1)](https://vachana.ai)
[![Gnani AI Timbre](https://img.shields.io/badge/Gnani%20Timbre-v3.0%20TTS-EC4899)](https://vachana.ai)
[![Framework: SYZYGY](https://img.shields.io/badge/Architecture-SYZYGY%20SDD%20v1.0-090D16)](https://github.com/atharveeee-netizen/syzygy)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📌 Executive Overview

**GallaVaani** bridges the digital divide between vernacular-speaking households in Tier 2/3 Indian towns and busy, non-typing neighborhood kirana shopkeepers (*Seth ji / Dukandar*).

Instead of forcing users to download bloated catalog apps (Blinkit, Zepto) or forcing shopkeepers to type inventory on a computer:
- **Customers** order by sending natural, noisy, code-mixed Hindi/vernacular WhatsApp voice notes ("Bhaiya 5kg Aashirvaad atta, pao bhar hari mirch, 10-wali 4 Maggi").
- **GallaVaani** normalizes colloquial measurements ("pao" $\rightarrow$ 250g, "10-wali" $\rightarrow$ MRP ₹10), resolves past-basket memories ("wahi pichli baar wali chai" $\rightarrow$ Tata Tea Agni 250g), and returns an Interactive WhatsApp Parchi paired with a 6-second synthesized Hindi readback voice note.
- **Shopkeepers** approve stock in **1.5 seconds** with a single tap (`[✅ Sab Hai - ₹380 Pack Karo]`), or swipe-to-reply with a 5-second voice override ("Aashirvaad khatam hai, Pillsbury rakh diya ₹240 ka").
- **Delivery Helpers (*Raju*)** receive a dispatch ticket on WhatsApp containing item counts, a dynamic doorstep UPI QR, and a playable 5-second customer landmark audio note ("Pani ki tanki ke peeche, hara gate").

**Zero App Installs. 100% WhatsApp Native.**

---

## ⚡ The 9 Concrete Engineering Breakthroughs

1. **Multi-Modal "Burst Coalescing" Customer Intake:** Customers often send an 18s voice note, followed immediately by a 2s text correction ("mirch pao nahi aadha kilo"), and a chit photo. An 8-second adaptive debounce window in Redis merges all fragments into a single unified Provisional Parchi.
2. **Dual-Modality "Speak & Show" Reply Cards:** Every customer card pairs an Interactive Button message with a synchronized 6-second native WhatsApp voice note (`voice: true` waveform via Gnani Timbre v3.0).
3. **The Shopkeeper's "Zero-Typing Parchi":** Happy path takes 1 tap (1.5 seconds). Stock changes take a 5-second swipe-to-reply voice note parsed via Gnani Prisma with `previous_text` lexical priming and our Cart Diff Engine.
4. **The "2-Strike Raw Audio Passthrough" (Zero-Drop Safety Net):** If an obscure local item has low ASR confidence ($<0.68$) after 1 retry, GallaVaani slices the exact 3-second audio snippet via FFmpeg, injects `[🎵 Voice Item #4 (Listen)]`, and forwards the raw audio directly to the shopkeeper's slip.
5. **Four-Rail Bharat Settlement Engine:** Supports neighborhood Bahi-Khata (Store Credit) with 2-word handover tokens ("Aam-24"), doorstep dynamic NPCI-compliant UPI QR codes, pre-dispatch UPI intent links for new callers, and COD change calculation advisories.
6. **Hybrid "Pin + Landmark Voice Clip" Address Vault:** Repeat callers are pre-filled via `wa_id`. First-timers share a WhatsApp location pin + 5s spoken landmark audio note. Both are attached to the delivery boy's dispatch card.
7. **Queue-Aware & Mohalla-Batched ETA Calculator:** Calculates accurate delivery ETAs based on items, radial mohalla zone rings, and active helper queue. Auto-batches neighbor orders placed within 12 minutes.
8. **75-Second "Galla Wake-Up" Escalation Protocol:** Solves counter notification blindness. If a confirmed order sits unread on WhatsApp for 75 seconds, an automated 10-second outbound IVR ring / soundbox chime alerts the merchant.
9. **Judge-Proof "Twin-Mode" Demo Architecture:** A split-screen Web Console that runs live with WhatsApp Cloud API, plus a 1-click deterministic local webhook injector with pre-recorded noisy voice notes for 0%-fail hackathon presentations.

---

## 🏛️ System Architecture

```
CUSTOMER WHATSAPP                    GALLAVAANI ENGINE (FASTAPI + REDIS)              SHOPKEEPER / RAJU WHATSAPP
─────────────────                    ───────────────────────────────────              ──────────────────────────
[18s Voice Note]  ──(Meta Webhook)──► • Redis Fast-Ack (<150ms)
                                      • 8s Burst Coalescer Buffer
                                      • Gnani Prisma v3.0 ASR (codemix)
                                      • Python Kirana Normalizer
                                      • Gnani Timbre v3.0 TTS
[Interactive Card + 6s Voice] ◄────── • Waveform Packager ("voice": true)

[Tap: ✅ Pakka Karo] ────────────────► • Lock Order #GV-204
                                      • Start 75s SLA Timer
                                      ────────────────(Shopkeeper Parchi)───────────► [1-Tap Approve Button]
                                                                                      OR [Swipe-to-Reply 5s Voice]
                                      ◄───────────────(5s Voice Diff)──────────────── 
                                      • Prisma ASR (previous_text primed)
                                      • Cart Diff Engine (Δ > ₹15 check)
                                      • Ephemeral 24h OOS Cache Update
[Substitution Card] ◄──────────────── • Auto-Approved / Customer Consent

[Tap: ✅ Haan Bhej Do] ──────────────► • Status: CONFIRMED_PACKING
                                      • Generate Signed NPCI Dynamic UPI QR
                                      • Route Raju Dispatch Ticket
[Cloned Voice Confirmation] ◄────────                                                 ◄── [Raju Dispatch Ticket
                                                                                          + Landmark Audio + UPI QR]
```

---

## 📁 The 8-File Spec-Driven Development (.spec/) Suite

GallaVaani's architecture strictly follows the **SYZYGY** Spec-Driven Development meta-framework. All foundational specifications are codified inside the [`.spec/`](.spec/) directory:

| Specification File | Purpose & Contents |
| :--- | :--- |
| [`.spec/PRD.md`](.spec/PRD.md) | **Product Requirements Document:** Problem statement, personas (Sunita Ji, Ramesh Seth, Raju), the 9 improvements, quantified SLAs, champion tool matrix, and MVP non-goals. |
| [`.spec/TechSpec.md`](.spec/TechSpec.md) | **Technical Specification:** Runtime toolchain (Python 3.11, FastAPI, Redis 7.2, PostgreSQL 16), Meta Cloud API v21.0+ pipeline, Gnani AI models (Prisma v3.0, Timbre v3.0), and hardware tiers. |
| [`.spec/Architecture.md`](.spec/Architecture.md) | **System Architecture:** Antonio Gulli's 66 Agentic Patterns via DeepSeek Harness (`dsh`), distributed Mermaid topology mesh, subagent definitions, and IPC contracts. |
| [`.spec/AppFlow.md`](.spec/AppFlow.md) | **Application Flow & Failure Register:** Complete end-to-end user journeys, Finite State Machine (FSM), 5 hard invariants, and the 10-cluster failure handling matrix. |
| [`.spec/Design.md`](.spec/Design.md) | **OpenDesign Contract:** Dark Obsidian tokens (`#090D16`), Outfit/Inter typography, spring physics, and WhatsApp template specifications (`customer_provisional_parchi`, etc.). |
| [`.spec/Rules.md`](.spec/Rules.md) | **Agent Directives & Security:** ASD-STE100 technical English constraints, banned marketing buzzwords, DPDP Act 2023 compliance, PII scrubbers, and 24h ephemeral audio TTL. |
| [`.spec/Schema.md`](.spec/Schema.md) | **Data Models & Protocols:** PostgreSQL DDL schemas (`orders`, `khata_ledger`, etc.), Redis key-spaces, OpenViking (`viking://`) URIs, and MCP JSON-RPC 2.0 tool definitions. |
| [`.spec/Tracker.md`](.spec/Tracker.md) | **Implementation Tracker:** Milestone tracking from M1 (Architecture) to M7 (Demo Hardening), along with pre-flight verification gates (ASD-STE100 and Strix Pentest). |

---

## 🤖 Gnani AI Model & Runtime Matrix

GallaVaani uses Gnani AI's hosted speech services coupled with deterministic slot extraction:

| Component | Model / Engine | Host / Endpoint | Role in GallaVaani |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text (ASR)** | **Prisma v3.0** | `api.vachana.ai/v1/stt` | Transcribes noisy Hinglish/vernacular WhatsApp `.ogg` voice notes with store `keyterms` and `previous_text`. |
| **Text-to-Speech (TTS)** | **Timbre v3.0** | `api.vachana.ai/v1/tts/sse` | Synthesizes normalized Hindi readback voice notes (`Shivani`/`Avinash`) with `"voice": true` waveforms. |
| **Unit Normalizer** | **Python Regex Engine** | In-Process / Zero Latency | Maps colloquial Indian quantities (`pao` $\rightarrow$ 250g, `sawa` $\rightarrow$ 1.25kg, `10-wali` $\rightarrow$ MRP 10) deterministically. |
| **Reasoning & Diff** | **Gemini 2.5 Flash / Evon v3.3** | Structured Tool-Calling | Handles ambiguous free-form conversational corrections and merchant diff calculations *(supports self-hosted Evon v3.3 via vLLM)*. |

> [!NOTE]
> **No Proprietary "Agent API" Required:** All subagents (`CustomerIntakeAgent`, `MerchantDiffAgent`, etc.) run as internal asynchronous workers orchestrated via Python/FastAPI.

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.11 or higher
- Redis 7.x (`redis-server`)
- PostgreSQL 16.x
- FFmpeg installed and available on `PATH`
- Meta for Developers account with WhatsApp Cloud API configured

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/usmedishetty/gnani-ul.git
cd gnani-ul

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)
Create a `.env` file in the root directory:
```dotenv
# Meta WhatsApp Cloud API
META_GRAPH_API_VERSION="v21.0"
WHATSAPP_PHONE_NUMBER_ID="your_meta_phone_number_id"
WHATSAPP_ACCESS_TOKEN="your_system_user_access_token"
WHATSAPP_VERIFY_TOKEN="gallavaani_secret_token"
WHATSAPP_APP_SECRET="your_meta_app_secret"

# Gnani AI Speech APIs
GNANI_API_KEY="your_gnani_api_key"
GNANI_PRISMA_ENDPOINT="https://api.vachana.ai/v1/stt"
GNANI_TIMBRE_ENDPOINT="https://api.vachana.ai/v1/tts/sse"

# Reasoning LLM (Fallback / Tool-Calling)
GEMINI_API_KEY="your_gemini_api_key"

# Database & Cache
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/gallavaani"
REDIS_URL="redis://localhost:6379/0"
```

### 4. Run the Local Backend & Webhook Tunnel
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start FastAPI Ingestion Gateway
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Expose Public Webhook for Meta
ngrok http 8000
```
In your **Meta App Dashboard** $\rightarrow$ **WhatsApp Configuration**, configure the Callback URL to:  
`https://<your-ngrok-subdomain>.ngrok-free.app/webhook/whatsapp`  
and subscribe to the **`messages`** webhook field.

---

## 🛡️ Hackathon Judge-Proof Twin-Mode Demo

During live presentations, conference Wi-Fi bottlenecks or Meta sandbox delays can stall live demos. GallaVaani includes a built-in **Judge Command Center**:

1. **Live WhatsApp Mode:** Send live voice notes from any smartphone to the WhatsApp test number.
2. **1-Click Local Webhook Injector:** Click `[⚡ Fire Pre-Recorded WhatsApp Payload]` on the dashboard to inject authentic noisy Indian voice notes directly into `/webhook/whatsapp`, executing live Gnani Prisma and Timbre calls on stage.
3. **Offline Golden Cache:** Failsafe toggle serving pre-cached SHA-256 matched speech responses in total internet blackouts.

---

## 📜 Standards & Compliance

- **DPDP Act 2023:** First-touch privacy notice and automated 24-hour ephemeral voice note deletion.
- **PII Scrubbing:** Regular expression scrubber masking OTPs, UPI PINs, and card numbers as `[REDACTED_SENSITIVE_DIGITS]`.
- **ASD-STE100:** Built without fluff or AI marketing buzzwords; all procedural statements adhere to Simplified Technical English.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
