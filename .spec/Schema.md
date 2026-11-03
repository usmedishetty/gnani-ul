# Schemas & Protocol Definitions (Schema.md)
## Project GallaVaani: Data Models, OpenViking URIs & JSON-RPC 2.0 Specifications

---

### 1. PostgreSQL Relational Schemas (DDL)

```sql
-- Core Merchant Table
CREATE TABLE merchants (
    merchant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_name VARCHAR(120) NOT NULL,
    shopkeeper_wa_id VARCHAR(20) UNIQUE NOT NULL,
    shopkeeper_name VARCHAR(80) NOT NULL,
    vpa_address VARCHAR(80) NOT NULL,
    vc_consent_verified BOOLEAN DEFAULT FALSE,
    vc_speaker_embedding_id VARCHAR(64),
    mohalla_zone VARCHAR(60) NOT NULL,
    daily_open_time TIME DEFAULT '07:00:00',
    daily_close_time TIME DEFAULT '22:30:00',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Registered Customers Table
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_id VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(80),
    preferred_language VARCHAR(10) DEFAULT 'hi-IN',
    trust_tier VARCHAR(20) DEFAULT 'NEW', -- NEW, TRUSTED, BLOCKED
    khata_enabled BOOLEAN DEFAULT FALSE,
    khata_limit NUMERIC(10, 2) DEFAULT 3000.00,
    current_khata_balance NUMERIC(10, 2) DEFAULT 0.00,
    dpdp_consent_granted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Hybrid Address Vault Table
CREATE TABLE customer_addresses (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_id VARCHAR(20) REFERENCES customers(wa_id) ON DELETE CASCADE,
    mohalla_zone VARCHAR(60) NOT NULL,
    landmark_text TEXT,
    landmark_audio_s3_url VARCHAR(255),
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    is_default BOOLEAN DEFAULT TRUE,
    verified_delivery_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders Table
CREATE TYPE order_status AS ENUM (
    'DRAFT_COLLECTING',
    'DRAFT_PAUSED',
    'AWAITING_SHOP_APPROVAL',
    'AWAITING_SUB_APPROVAL',
    'CONFIRMED_PACKING',
    'OUT_FOR_DELIVERY',
    'DELIVERED_SETTLED',
    'CANCELLED'
);

CREATE TYPE payment_rail AS ENUM (
    'BAHI_KHATA',
    'QR_ON_DELIVERY',
    'PREPAY_UPI',
    'COD'
);

CREATE TABLE orders (
    order_id VARCHAR(32) PRIMARY KEY, -- e.g. GV-204
    cart_version_id INT NOT NULL DEFAULT 1,
    merchant_id UUID REFERENCES merchants(merchant_id),
    customer_wa_id VARCHAR(20) REFERENCES customers(wa_id),
    status order_status NOT NULL DEFAULT 'DRAFT_COLLECTING',
    payment_mode payment_rail NOT NULL DEFAULT 'QR_ON_DELIVERY',
    payment_status VARCHAR(20) DEFAULT 'UNPAID', -- UNPAID, PAID, CREDITED
    indicative_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    final_total NUMERIC(10, 2),
    khata_handover_code VARCHAR(16),
    upi_txn_ref VARCHAR(64),
    delivery_helper_wa_id VARCHAR(20),
    helper_assigned_at TIMESTAMPTZ,
    calculated_eta_minutes INT,
    merchant_approval_event_id VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Order Items Table
CREATE TYPE sku_kind AS ENUM (
    'STANDARD_SKU',
    'PRICE_POINT_PACK',
    'VALUE_LOCKED_LOOSE',
    'VOICE_PASSTHROUGH_SKU'
);

CREATE TABLE order_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(32) REFERENCES orders(order_id) ON DELETE CASCADE,
    line_index INT NOT NULL,
    raw_spoken_text TEXT NOT NULL,
    normalized_sku_name VARCHAR(120),
    kind sku_kind NOT NULL DEFAULT 'STANDARD_SKU',
    requested_quantity NUMERIC(8, 3),
    unit VARCHAR(20), -- kg, g, pcs, packet, liter
    unit_price NUMERIC(10, 2),
    line_total NUMERIC(10, 2) NOT NULL,
    asr_confidence NUMERIC(4, 3) NOT NULL,
    audio_clip_s3_url VARCHAR(255), -- Populated for VOICE_PASSTHROUGH_SKU
    is_substituted BOOLEAN DEFAULT FALSE,
    substituted_from_sku VARCHAR(120),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Digital Bahi-Khata Ledger Table
CREATE TABLE khata_ledger (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_wa_id VARCHAR(20) REFERENCES customers(wa_id),
    merchant_id UUID REFERENCES merchants(merchant_id),
    order_id VARCHAR(32) REFERENCES orders(order_id),
    txn_type VARCHAR(10) NOT NULL, -- DEBIT, CREDIT
    amount NUMERIC(10, 2) NOT NULL,
    balance_after NUMERIC(10, 2) NOT NULL,
    handover_token_verified VARCHAR(16),
    audit_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ephemeral Out-of-Stock Tracking Table
CREATE TABLE ephemeral_oos_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(merchant_id),
    sku_token VARCHAR(120) NOT NULL,
    flagged_order_id VARCHAR(32),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(merchant_id, sku_token)
);

-- Immutable Security & Audit Log Table
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    entity_name VARCHAR(40) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(60) NOT NULL,
    actor_wa_id VARCHAR(20) NOT NULL,
    event_payload JSONB NOT NULL,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2. Redis Key-Space & In-Memory TTL Architecture

```
┌──────────────────────────────────────┬────────────────┬──────────────┬───────────────────────────────────────────┐
│ Redis Key Pattern                    │ Data Structure │ Default TTL  │ Purpose / Function                        │
├──────────────────────────────────────┼────────────────┼──────────────┼───────────────────────────────────────────┤
│ `wamid:{message_id}`                 │ String (Flag)  │ 86400s (24h) │ Prevents duplicate Meta webhook ingestion │
│ `inbox:{customer_wa_id}`             │ List / Hash    │ 120s         │ Buffers 8s customer multi-modal bursts    │
│ `debounce_lock:{customer_wa_id}`     │ String         │ 8s           │ Sliding window timer for burst intake     │
│ `csw:{customer_wa_id}`               │ String (Epoch) │ 86400s (24h) │ Tracks Meta 24h Customer Service Window   │
│ `sla_timers`                         │ Sorted Set     │ Persistent   │ Monitored by Galla Wake-Up 75s daemon     │
│ `ephemeral_oos:{merchant_id}`        │ Set of Strings │ Midnight TTL │ Out-of-Stock SKUs learned today           │
│ `cart:{order_id}`                    │ Hash           │ 86400s (24h) │ Active in-flight order state cache        │
│ `audio_cache:{sha256}`               │ Hash (Binary)  │ 604800s (7d) │ Offline golden speech responses for demo  │
└──────────────────────────────────────┴────────────────┴──────────────┴───────────────────────────────────────────┘
```

---

### 3. OpenViking Memory URI Space (`viking://`)

GallaVaani structures its persistent agent memory hierarchy using **OpenViking** URI namespace:

```text
viking://[domain]/[namespace]/[resource_id]
```

- **Active Session:** `viking://session/active/{sessionId}` — In-flight multi-agent coordination graph, active debounce buffers, and subagent state.
- **Store Catalog:** `viking://store/{merchant_id}/catalog` — Top 100 SKUs, custom fractional prices, and colloquial commodity keyterms.
- **Daily Stock Cache:** `viking://store/{merchant_id}/oos_cache` — Ephemeral out-of-stock items learned from merchant voice diffs.
- **Customer History:** `viking://customer/{wa_id}/history` — Previous 5 completed baskets, habitual brand preferences (e.g., `"wahi pichli baar wali chai"` $\rightarrow$ `Tata Tea Agni 250g`).
- **Raw Audio Passthrough:** `viking://audio/passthrough/{order_id}/{item_index}` — Sliced 3-second `.ogg` audio clips for unverified regional brands.
- **Speech Telemetry:** `viking://telemetry/gnani/{call_id}` — Latency metrics, SNR ratios, and confidence scores across Prisma and Timbre calls.

---

### 4. Model Context Protocol (MCP) JSON-RPC 2.0 Invocations

#### 4.1 Tool 1: `gnani_prisma_transcribe`
```json
{
  "jsonrpc": "2.0",
  "id": "tool-call-prisma-01",
  "method": "gnani_prisma_transcribe",
  "params": {
    "audio_base64": "GkXfo59ChoEBQveBAULygQETH4Bi...",
    "format": "codemix",
    "lang_code": "indic-auto",
    "speech_enhancement": true,
    "keyterms": [
      "Aashirvaad", "Pillsbury", "pao", "adhpao", "sawa kilo",
      "dedh kilo", "Maggi", "Agni chai", "Kaka namkeen"
    ],
    "previous_text": "Aashirvaad Atta 5kg, Hari Mirch 250g, Maggi 4 pcs"
  }
}
```

#### 4.2 Tool 2: `gnani_timbre_synthesize`
```json
{
  "jsonrpc": "2.0",
  "id": "tool-call-timbre-02",
  "method": "gnani_timbre_synthesize",
  "params": {
    "normalized_text": "Kul paanch item. Andazan bill chaar sau painsath rupaye. Pata Awas Vikas Gate do.",
    "voice_profile": "Shivani",
    "output_format": "audio/ogg; codecs=opus",
    "expressive_tags": true,
    "whatsapp_waveform": true
  }
}
```

#### 4.3 Tool 3: `cart_diff_engine`
```json
{
  "jsonrpc": "2.0",
  "id": "tool-call-diff-03",
  "method": "cart_diff_engine",
  "params": {
    "order_id": "GV-204",
    "current_cart": [
      {"name": "Aashirvaad Atta", "qty": 5.0, "unit": "kg", "price": 255.0},
      {"name": "Hari Mirch", "qty": 0.25, "unit": "kg", "price": 20.0}
    ],
    "shopkeeper_transcript": "Aashirvaad paanch kilo khatam hai, Pillsbury rakh diya do sau chaalis ka aur mirch pandrah rupaye ki",
    "tolerance_threshold_rupees": 15.0
  }
}
```

#### 4.4 Tool 4: `settlement_generate_qr`
```json
{
  "jsonrpc": "2.0",
  "id": "tool-call-settle-04",
  "method": "settlement_generate_qr",
  "params": {
    "order_id": "GV-204",
    "merchant_vpa": "sharmastore@icici",
    "merchant_name": "Sharma Provision Store",
    "amount": 365.00,
    "currency": "INR",
    "format": "PNG",
    "dimension_px": 512
  }
}
```
