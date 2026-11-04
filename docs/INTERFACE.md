# GallaVaani Pipeline Data & Error Interface Contracts
> **Specification Version:** 1.0.0 (Phase 0 Baseline)  
> **Target Stack:** Python 3.11+, Pydantic v2, FastAPI, Gnani AI (Prisma v3.0 / Timbre v3.0)  

---

## 1. Architectural Pipeline Flow

```
[Audio Bytes (OGG/Opus)]
         │
         ▼  (1. STT Service / Gnani Prisma v3.0)
[STTResponse (Transcript + Confidence + Word Spans)]
         │
         ▼  (2. Intent & Normalization Engine)
[CartIntentResult (Normalized SKUs + Quantities + Totals)]
         │
         ▼  (3. Merchant Diff / State Machine)
[OrderCart & DiffResult (Approved or Mutated Cart)]
         │
         ▼  (4. Response Formatter)
[ParchiTextPayload (Interactive WhatsApp Card + Script)]
         │
         ▼  (5. TTS Service / Gnani Timbre v3.0)
[TTSResponse (Synthesized Audio Bytes - OGG/Opus)]
```

---

## 2. Interface Contracts & Data Shapes (Pydantic v2 Models)

### 2.1 Audio Ingress (`AudioPayload`)
Represents incoming raw audio from Meta WhatsApp Cloud API or local replay injector.

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class AudioPayload(BaseModel):
    audio_bytes: bytes = Field(..., description="Raw binary audio payload")
    mime_type: Literal["audio/ogg; codecs=opus", "audio/ogg", "audio/wav", "audio/mp3", "audio/m4a"] = Field(
        default="audio/ogg; codecs=opus",
        description="MIME type of incoming audio"
    )
    duration_ms: Optional[int] = Field(None, ge=100, le=120000, description="Audio duration in milliseconds")
    sample_rate_hz: int = Field(default=16000, description="Sampling rate in Hz")
    channels: int = Field(default=1, ge=1, le=2, description="Channel count (1=mono, 2=stereo)")
    source: Literal["whatsapp_webhook", "twin_mode_injector", "test_fixture"] = Field(
        default="whatsapp_webhook"
    )
    wamid: Optional[str] = Field(None, description="Unique WhatsApp message ID if from webhook")
```

---

### 2.2 STT Contract: Gnani Prisma v3.0 (`STTRequest` & `STTResponse`)

```python
class WordTimestamp(BaseModel):
    word: str
    start_time_ms: int
    end_time_ms: int
    confidence: float = Field(ge=0.0, le=1.0)

class STTRequest(BaseModel):
    audio_bytes: bytes
    lang_code: str = Field(default="hi-IN", description="Target Indic language code")
    format_type: Literal["codemix", "standard"] = Field(default="codemix")
    speech_enhancement: bool = Field(default=True, description="Enable background noise stripping")
    keyterms: list[str] = Field(default_factory=list, max_length=100, description="Contextual store SKUs & units")
    previous_text: Optional[str] = Field(None, description="Cart conditioning text for voice diffs")

class STTResponse(BaseModel):
    transcript: str = Field(..., description="Cleaned, transcribed text")
    raw_transcript: str = Field(..., description="Raw ASR hypothesis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall utterance confidence score")
    detected_language: str = Field(default="hi-IN")
    duration_sec: float = Field(..., ge=0.0)
    word_timestamps: list[WordTimestamp] = Field(default_factory=list)
    is_fallback: bool = Field(default=False, description="True if served via mock or golden cache")
```

---

### 2.3 Intent Extraction & Normalization Contract (`CartIntentResult`)

```python
from enum import Enum
from decimal import Decimal

class SKUKind(str, Enum):
    STANDARD_SKU = "STANDARD_SKU"
    PRICE_POINT_PACK = "PRICE_POINT_PACK"
    VALUE_LOCKED_LOOSE = "VALUE_LOCKED_LOOSE"
    VOICE_PASSTHROUGH_SKU = "VOICE_PASSTHROUGH_SKU"

class CartItem(BaseModel):
    line_index: int
    raw_spoken_text: str
    normalized_sku_name: str
    kind: SKUKind = SKUKind.STANDARD_SKU
    requested_quantity: Decimal = Field(..., decimal_places=3, ge=Decimal("0.001"))
    unit: str = Field(..., description="kg, g, pcs, packet, liter")
    unit_price: Decimal = Field(..., decimal_places=2, ge=Decimal("0.00"))
    line_total: Decimal = Field(..., decimal_places=2, ge=Decimal("0.00"))
    asr_confidence: float = Field(ge=0.0, le=1.0)
    audio_slice_path: Optional[str] = Field(None, description="Path to 3s audio snippet if low confidence")
    is_substituted: bool = False
    substituted_from_sku: Optional[str] = None

class UnresolvedSpan(BaseModel):
    raw_text: str
    start_time_ms: Optional[int] = None
    end_time_ms: Optional[int] = None
    confidence: float
    reason: Literal["low_confidence", "unknown_brand", "missing_quantity"]

class CartIntentResult(BaseModel):
    items: list[CartItem]
    unresolved_items: list[UnresolvedSpan] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    indicative_total: Decimal = Field(..., decimal_places=2)
    applied_assumptions: list[str] = Field(default_factory=list)
```

---

### 2.4 Merchant Diff Contract (`CartDiffResult`)

```python
class SubstitutionAction(str, Enum):
    NO_CHANGE = "NO_CHANGE"
    PRICE_ADJUSTED = "PRICE_ADJUSTED"
    BRAND_SWAPPED = "BRAND_SWAPPED"
    PACK_SPLIT = "PACK_SPLIT"
    ITEM_REMOVED = "ITEM_REMOVED"
    ITEM_ADDED = "ITEM_ADDED"

class ItemDiff(BaseModel):
    action: SubstitutionAction
    original_item: Optional[CartItem] = None
    updated_item: Optional[CartItem] = None
    price_delta: Decimal = Decimal("0.00")
    reason: Optional[str] = None

class CartDiffResult(BaseModel):
    order_id: str
    previous_cart_version: int
    new_cart_version: int
    diffs: list[ItemDiff]
    net_price_delta: Decimal = Decimal("0.00")
    requires_customer_consent: bool = Field(
        ...,
        description="True if net price delta > ₹15 or any brand substitution occurred (Invariant 2)"
    )
    final_total: Decimal = Field(..., decimal_places=2)
    ephemeral_oos_skus: list[str] = Field(
        default_factory=list,
        description="SKUs to add to 24-hour merchant out-of-stock cache"
    )
```

---

### 2.5 Presentation Parchi Contract (`ParchiTextPayload`)

```python
class ParchiButton(BaseModel):
    id: str
    title: str = Field(..., max_length=20)
    payload: str

class ParchiTextPayload(BaseModel):
    order_id: str
    recipient_wa_id: str
    role: Literal["customer", "shopkeeper", "raju"]
    header_text: str
    body_text: str
    footer_text: Optional[str] = None
    buttons: list[ParchiButton] = Field(default_factory=list, max_length=3)
    spoken_script_hindi: str = Field(..., description="Phonetically expanded Hindi script for TTS synthesis")
```

---

### 2.6 TTS Contract: Gnani Timbre v3.0 (`TTSRequest` & `TTSResponse`)

```python
class TTSRequest(BaseModel):
    normalized_text: str = Field(..., description="Expanded text e.g. 'chaar sau painsath rupaye'")
    voice_profile: Literal["Shivani", "Avinash"] = Field(default="Shivani")
    lang_code: str = Field(default="hi-IN")
    output_format: Literal["audio/ogg; codecs=opus", "audio/wav"] = Field(default="audio/ogg; codecs=opus")
    whatsapp_waveform: bool = Field(default=True, description="Sets voice: true flag for WhatsApp player")

class TTSResponse(BaseModel):
    audio_bytes: bytes
    mime_type: str = "audio/ogg; codecs=opus"
    duration_sec: float
    voice_profile_used: str
    is_fallback: bool = False
```

---

## 3. Explicit Error Shapes & Failure Enums

```python
class ErrorCode(str, Enum):
    # Ingress / Audio
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    AUDIO_TOO_SHORT = "AUDIO_TOO_SHORT"
    DUPLICATE_WAMID = "DUPLICATE_WAMID"

    # STT / Gnani Prisma
    GNANI_AUTH_FAILED = "GNANI_AUTH_FAILED"
    GNANI_RATE_LIMITED = "GNANI_RATE_LIMITED"
    GNANI_TIMEOUT = "GNANI_TIMEOUT"
    GNANI_SERVER_ERROR = "GNANI_SERVER_ERROR"
    LOW_CONFIDENCE_THRESHOLD = "LOW_CONFIDENCE_THRESHOLD"

    # FSM / State Invariants
    INVARIANT_UNVERIFIED_DISPATCH = "INVARIANT_UNVERIFIED_DISPATCH"
    INVARIANT_SILENT_UPCHARGE = "INVARIANT_SILENT_UPCHARGE"
    INVARIANT_STALE_CART_VERSION = "INVARIANT_STALE_CART_VERSION"
    INVARIANT_IMMUTABLE_SETTLED = "INVARIANT_IMMUTABLE_SETTLED"
    INVARIANT_POST_DISPATCH_CANCEL = "INVARIANT_POST_DISPATCH_CANCEL"

    # TTS / Gnani Timbre
    TTS_SYNTHESIS_FAILED = "TTS_SYNTHESIS_FAILED"
    TTS_TIMEOUT = "TTS_TIMEOUT"

class PipelineError(Exception):
    def __init__(self, code: ErrorCode, message: str, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")

class ErrorEnvelope(BaseModel):
    success: Literal[False] = False
    error_code: ErrorCode
    message: str
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

