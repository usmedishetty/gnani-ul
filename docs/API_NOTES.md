# GallaVaani API Ground Truth & Integration Notes (docs/API_NOTES.md)

> **Status:** Ground Truth Specification  
> **Source Validation:** Verified via official documentation (`vachana.ai`, `docs.vachana.ai`, Meta for Developers Graph API v21.0+)  
> **Last Verified:** November 4, 2026  

---

## 1. Gnani AI Speech-to-Text (ASR) — Prisma v3.0

### 1.1 Verified Endpoint & Transport
* **Base URL:** `https://api.vachana.ai`
* **REST Endpoint:** `POST https://api.vachana.ai/stt/v3`
* **Realtime Streaming Protocol:** `wss://api.vachana.ai/stt/v3/stream` (Raw PCM16 mono, 16 kHz LE)
* **Authentication Header:**
  ```http
  X-API-Key-ID: <GNANI_API_KEY>
  ```
  *(Important: Do NOT pass Bearer token or `Authorization` header. Header name must be exact: `X-API-Key-ID`)*.

### 1.2 Request Payload Specification (Multipart Form-Data)
| Field | Type | Required | Description | Allowed Values |
|---|---|---|---|---|
| `audio_file` | Binary File | **Yes** | Raw audio file stream. | OGG (`audio/ogg`), Opus, WAV, MP3, FLAC, AAC, M4A |
| `model` | String | **Yes** | Target ASR acoustic model. | `prisma-v3.0` (default / recommended), `prisma-v2.5` |
| `language_code`| String | **Yes** | Indic language code hint or pairing. | Single (`hi-IN`, `kn-IN`, `mr-IN`, `gu-IN`), Comma-pair (`hi-IN,en-IN`), or `indic-auto` |
| `format` | String | No | Transcript normalization mode. | `codemix` (keeps English in Latin script, Indic in Devanagari), `transcribe` (ITN enabled), `verbatim`, `transliterate` |
| `keyterms` | JSON Array / String | No | Up to 100 domain vocabulary terms for acoustic biasing. | e.g. `'["Aashirvaad", "Pillsbury", "pao", "10-wali", "Maggi"]'` |
| `previous_text`| String | No | Prior conversational context for lexical conditioning. | e.g. `"Aashirvaad Atta 5kg, Hari Mirch 250g"` (Crucial for shopkeeper diffs) |

### 1.3 Response Schema (JSON)
```json
{
  "transcript": "bhaiya paanch kilo aashirvaad atta aur pao bhar hari mirch",
  "confidence": 0.942,
  "language_detected": "hi-IN",
  "duration_seconds": 4.82,
  "words": [
    {"word": "bhaiya", "start": 0.20, "end": 0.65, "confidence": 0.96},
    {"word": "paanch", "start": 0.70, "end": 1.10, "confidence": 0.95},
    {"word": "kilo", "start": 1.12, "end": 1.45, "confidence": 0.98},
    {"word": "aashirvaad", "start": 1.50, "end": 2.15, "confidence": 0.94},
    {"word": "atta", "start": 2.20, "end": 2.60, "confidence": 0.93}
  ]
}
```

### 1.4 Limits & Constraints
* **Max Audio Duration:** Standard REST endpoint is optimized for clips $\le 30\text{ seconds}$ (hard ceiling 60 seconds). For WhatsApp clips $>30\text{s}$, slice at silence intervals using `ffmpeg`.
* **Rate Limits:** HTTP `429 Too Many Requests` triggered upon exceeding concurrent stream or request-per-second thresholds. Handled via exponential backoff (200ms, 600ms, 1500ms).
* **Credit Consumption:** Metered per audio second transcribed against prepaid pool (5,000 credit hackathon allotment).

---

## 2. Gnani AI Text-to-Speech (TTS) — Timbre v3.0

### 2.1 Verified Endpoints & Transport
* **REST Inference Endpoint:** `POST https://api.vachana.ai/api/v1/tts/inference`
* **SSE Streaming Endpoint:** `POST https://api.vachana.ai/api/v1/tts/sse`
* **Authentication Header:**
  ```http
  X-API-Key-ID: <GNANI_API_KEY>
  Content-Type: application/json
  ```

### 2.2 Request Payload Specification (JSON)
```json
{
  "text": "नमस्ते, आपका कुल बिल तीन सौ अस्सी रुपये है।",
  "model": "timbre-v3.0",
  "voice": "Nalini",
  "language": "hi-IN",
  "speed": 1.0,
  "audio_config": {
    "sample_rate": 22050,
    "encoding": "linear_pcm",
    "container": "wav"
  }
}
```

### 2.3 Verified Voice Profiles
* `timbre-v3.0`: Multilingual neural models where each speaker persona speaks across all supported Indic languages:
  * Female profiles: `Nalini`, `Kaveri`, `Shivani`
  * Male profiles: `Deepak`, `Avinash`
* *Note:* Voices are bound to model versions (`timbre-v3.0` voices cannot be passed to `timbre-v2.5` requests).

### 2.4 WhatsApp Audio Formatting (OGG/Opus Mono)
* Meta WhatsApp Cloud API requires native voice messages to be encoded as:
  * Container: OGG
  * Audio Codec: Opus
  * Channels: Mono (1 channel)
  * Sample Rate: 16,000 Hz (or 24,000 Hz)
* If Timbre returns WAV or PCM, GallaVaani transcodes the stream via `ffmpeg`:
  ```bash
  ffmpeg -i input.wav -c:a libopus -b:a 24k -ar 16000 -ac 1 output.ogg
  ```

---

## 3. Meta WhatsApp Cloud API (v21.0+)

### 3.1 Webhook Verification (GET)
* **Endpoint:** `GET /webhook/whatsapp`
* **Query Parameters:**
  * `hub.mode`: Must equal `"subscribe"`
  * `hub.verify_token`: Must match `WHATSAPP_VERIFY_TOKEN` in `.env`
  * `hub.challenge`: Plain integer string that must be reflected in HTTP 200 response.

### 3.2 Webhook Ingestion & Signature (POST)
* **Endpoint:** `POST /webhook/whatsapp`
* **Header:** `X-Hub-Signature-256: sha256=<HMAC>`
* **Validation:** Computed using HMAC-SHA256 over raw request body using `WHATSAPP_APP_SECRET`.
* **Idempotency:** Unique message ID extracted from `entry[0].changes[0].value.messages[0].id`. Must execute Redis `SETNX wamid:{id} 1 EX 86400` and respond with `HTTP 200 OK` within $<150\text{ ms}$.

### 3.3 Ephemeral Media Retrieval
1. Inbound message carries `media_id` (e.g., `messages[0].audio.id`).
2. Query Meta Graph API for temporary download URL:
   ```http
   GET https://graph.facebook.com/v21.0/{media_id}
   Authorization: Bearer <WHATSAPP_ACCESS_TOKEN>
   ```
3. Fetch raw binary stream from returned `url` with `Authorization: Bearer <WHATSAPP_ACCESS_TOKEN>`.
4. URL expires in 5 minutes; binary must be held in memory or cached ephemerally.

### 3.4 Outbound Message Dispatch
* **Endpoint:** `POST https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages`
* **Header:** `Authorization: Bearer <WHATSAPP_ACCESS_TOKEN>`, `Content-Type: application/json`
* **Interactive Button Message Example:**
  ```json
  {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "+9198XXXXXXXX",
    "type": "interactive",
    "interactive": {
      "type": "button",
      "header": {"type": "text", "text": "🧾 Sharma Store - Kacchi Parchi #204"},
      "body": {"text": "1. Aashirvaad Atta (5kg) — ₹255\n2. Hari Mirch (250g) — ₹20\n\nTotal: ~₹275"},
      "action": {
        "buttons": [
          {"type": "reply", "reply": {"id": "CONFIRM_GV204_V1", "title": "✅ Pakka Karo"}},
          {"type": "reply", "reply": {"id": "MUTATE_GV204_V1", "title": "🎙️ Badlo"}}
        ]
      }
    }
  }
  ```
* **Native Voice Note Dispatch Example (`"voice": true`):**
  ```json
  {
    "messaging_product": "whatsapp",
    "to": "+9198XXXXXXXX",
    "type": "audio",
    "audio": {
      "id": "<UPLOADED_MEDIA_ID>",
      "voice": true
    }
  }
  ```

---

## 4. Discrepancy & Conflict Register Between Doc Pages

| # | Topic | Discrepancy Found in Docs | Ground Truth Resolution for GallaVaani |
|---|---|---|---|
| **D1** | **STT Endpoint URI** | Some older Gnani tutorials mention `POST /v1/stt` or `POST /api/v1/stt`; newer vachana.ai documentation specifies `POST /stt/v3`. | Use `POST https://api.vachana.ai/stt/v3`. Confirmed via vachana.ai v3 API schema. |
| **D2** | **Auth Header Name** | Generic OpenAPI examples suggest `Authorization: Bearer <token>`; vachana.ai gateway specifically requires `X-API-Key-ID: <token>`. | Standardize on header `X-API-Key-ID`. Do NOT use `Authorization` header for Gnani endpoints. |
| **D3** | **`format` Availability** | Older `prisma-v2.5` only supported `verbatim` and `transcribe`; `codemix` and `transliterate` are exclusive to `prisma-v3.0`. | Always pass `model=prisma-v3.0` whenever `format="codemix"` is specified. |
| **D4** | **TTS Endpoint Structure** | Some docs list `/tts/v3` or `/v1/tts/synthesize`; active production routes are `/api/v1/tts/inference` (REST) and `/api/v1/tts/sse` (Streaming). | Use `POST /api/v1/tts/inference` for synchronous batch clips and `/api/v1/tts/sse` for streaming chunk playback. |
| **D5** | **Voice Compatibility** | Documentation displays mixed voice names (`Shivani`, `Avinash`, `Nalini`, `Kaveri`, `Deepak`). | Voices are model-partitioned. For `timbre-v3.0`, use `Nalini` or `Deepak` (or `Shivani`/`Avinash` if provisioned on account). Verify via `smoke_test_gnani`. |
| **D6** | **Voice Cloning (`vachana-vc-v1`)** | Listed under experimental research docs, but not available on standard public API tiers. | Excluded from MVP (CUT). Replaced with pre-configured Timbre neural voices. |

---

## 5. Token & Credit Economics

* **Allotted Account Pool:** 5,000 Credits.
* **Per-Order Intake Cost:**
  * 1x 15s Customer Voice Note ASR $\approx$ ₹0.25 (metered credits).
  * 1x 6s Parchi Readback TTS $\approx$ ₹0.15 (metered credits).
  * WhatsApp 24h Customer Service Window (CSW): Free-form interactive messages inside 24h window incur **zero Meta conversation fees**.
* **Zero Credit Development Policy:**
  * All unit and integration test runs must use recorded fixtures in `tests/fixtures/`.
  * Live API calls are strictly restricted to phase gates (`pytest -m live`) and initial smoke tests to preserve credit runway.
