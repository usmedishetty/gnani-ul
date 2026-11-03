# OpenDesign Contract (Design.md)
## Project GallaVaani: WhatsApp Design Language & Judge Console UI Contract

---

### 1. OpenDesign Visual Philosophy

GallaVaani enforces the **OpenDesign `DESIGN.md`** contract to eliminate unstyled defaults and low-contrast AI slop. It defines design standards across two distinct display surfaces:
1. **The Judge Command Center:** Dark Obsidian high-density monitoring interface for hackathon juries and store administrators.
2. **WhatsApp Native Conversational Cards:** High-contrast Unicode text cards, bolded metric tokens, and localized Devanagari microcopy structured for small budget smartphone screens in Tier 2/3 markets.

---

### 2. Design Tokens & CSS Variables

```css
:root {
  /* Surface Tokens (Dark Obsidian Canvas) */
  --bg-primary: #090d16;             /* Deep Space Obsidian */
  --bg-surface: #0f172a;             /* Slate 900 Surface Card */
  --bg-surface-hover: #1e293b;       /* Slate 800 Interactive Hover */
  --bg-surface-elevated: #1e293b;    /* Elevated Modal & Flyout */

  /* Border & Stroke Tokens */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-active: rgba(99, 102, 241, 0.35);
  --border-focus: #6366f1;

  /* Typography Colors */
  --text-primary: #f8fafc;           /* Slate 50 (High Contrast) */
  --text-muted: #94a3b8;             /* Slate 400 (Metadata & Timestamps) */
  --text-dim: #64748b;               /* Slate 500 (Disabled Elements) */

  /* Brand & Domain Accent Tokens */
  --accent-primary: #6366f1;         /* Indigo 500 (Core Brand) */
  --accent-glow: rgba(99, 102, 241, 0.25);
  --brand-whatsapp: #25d366;         /* WhatsApp Emerald */
  --brand-whatsapp-dim: rgba(37, 211, 102, 0.15);
  --brand-upi: #00a3ff;              /* Bharat NPCI UPI Cyan */
  --status-warning: #f59e0b;         /* Amber 500 (Substitutions & 75s SLA) */
  --status-danger: #ef4444;          /* Red 500 (Out-of-Stock & Rejections) */
  --status-success: #10b981;         /* Emerald 500 (Delivered & Verified) */
}
```

---

### 3. Typography & Microcopy Hierarchy

#### 3.1 Web Dashboard (Judge Command Center)
- **Title Font:** `Outfit`, sans-serif (Weights: 600, 700) — clean geometric headers.
- **Body Font:** `Inter`, sans-serif (Weights: 400, 500) — high-legibility interface copy.
- **Monospace Code Font:** `JetBrains Mono`, monospace (Weight: 500) — JSON payload inspection, webhook streams, and latency metrics.

#### 3.2 Conversational WhatsApp Typography
- **Language Stack:** Latin + Devanagari Unicode (`Noto Sans Devanagari`).
- **Formatting Constraints:** Bold line-item identifiers (`*1. Aashirvaad Atta (5 kg)*`), monospace order IDs (`#GV-204`), and clear section dividers (`━━━━━━━━━━━━━━`).
- **Button Microcopy Rules:** Maximum 20 characters per button title. Always pair an unambiguous emoji with active vernacular Hindi verbs (`[✅ Order Pakka Karo]`, `[🎙️ Badlo / Jodo]`, `[💳 Payment/Pata]`).

---

### 4. WhatsApp Template UI Card Design Specifications

#### 4.1 Customer Provisional Parchi (`customer_provisional_parchi`)
- **Type:** Free-form Interactive Button Message inside 24h CSW + Native Timbre v3.0 Voice Note (`voice: true`).
- **Layout Structure:**
  ```text
  🧾 *Sharma Store - Kacchi Parchi #204*
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. *Aashirvaad Atta (5 kg)* — ~₹255
  2. *Hari Mirch (250g / Pao)* — ~₹20
  3. *Maggi 10-Wali (x4)* — ₹40
  4. *Tata Tea Agni (250g)* — ₹65
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💰 *Andazan Bill: ~₹380*
  📍 *Pata:* Awas Vikas Gate 2
  💳 *Mode:* Bahi-Khata (Bal: ₹1,120)
  
  _Stock confirm hone par pakka bill aayega_
  ```
- **Action Buttons:**
  - Button 1: `[✅ Order Pakka Karo]` (Payload: `CONFIRM_GV204_V1`)
  - Button 2: `[🎙️ Badlo / Jodo]` (Payload: `MUTATE_GV204_V1`)
  - Button 3: `[💳 Payment/Pata]` (Payload: `SETTINGS_GV204_V1`)

#### 4.2 Shopkeeper Counter Parchi (`shopkeeper_counter_parchi`)
- **Type:** Utility Template (`galla_new_order_v1`) + Forwarded Cropped Audio Snippets.
- **Layout Structure:**
  ```text
  🔔 *NAYA ORDER #204 (Sunita Ji)*
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡ *[BATCH: AWAS VIKAS - WITH #201]*
  • Aashirvaad Atta — 5 kg (₹255)
  • Hari Mirch — 250g (₹20)
  • Maggi ₹10 Pack — 4 pcs (₹40)
  • Tata Tea Agni — 250g (₹65)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💵 *Total: ₹380 (KHATA - Bal: ₹1,120)*
  
  _Badlav ke liye is message par Mic daba ke bolen_
  ```
- **Action Buttons:**
  - Button 1: `[✅ Sab Hai (₹380)]` (Payload: `APPROVE_GV204`)
  - Button 2: `[⏱️ 30m Baad Bhejenge]` (Payload: `DELAY_30_GV204`)
  - Button 3: `[📞 Call Customer]` (Payload: `CALL_GV204`)

#### 4.3 Customer Substitution Approval (`customer_sub_approval`)
- **Type:** Free-form Interactive Button Message + Timbre v3.0 Audio Diff.
- **Layout Structure:**
  ```text
  🔄 *Chhota Badlav - Order #204*
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sharma ji ne bataya:
  ❌ Aashirvaad 5kg abhi khatam hai
  ✅ Badle mein: Pillsbury 5kg (₹240)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💰 *Naya Pakka Bill: ₹365*
  🚚 *ETA: ~20 mins*
  ```
- **Action Buttons:**
  - Button 1: `[✅ Haan Bhej Do]` (Payload: `ACCEPT_SUB_GV204`)
  - Button 2: `[⏭️ Yeh Item Hata Do]` (Payload: `DROP_ITEM_GV204`)
  - Button 3: `[❌ Order Cancel]` (Payload: `CANCEL_GV204`)

#### 4.4 Raju Delivery Ticket (`raju_delivery_ticket`)
- **Type:** Free-form Interactive Message + Attached Landmark Voice Clip + Dynamic UPI QR.
- **Layout Structure:**
  ```text
  🛵 *DELIVERY #204 — Awas Vikas*
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  👤 *Sunita Ji* (+91-98XXXXXX12)
  📍 *Pani ki tanki ke peeche, Gate 2*
  📦 *4 Items (1 Thaila)*
  💳 *Lena Hai: ₹365 (UPI QR ya Cash)*
  🔑 *Khata Code: AAM-24*
  ```
- **Action Buttons:**
  - Button 1: `[🔳 Show ₹365 QR]` (Payload: `SHOW_QR_GV204`)
  - Button 2: `[✅ Delivered]` (Payload: `DELIVERED_GV204`)
  - Button 3: `[⚠️ Ghar Nahi Mila]` (Payload: `HELP_LOCATION_GV204`)

---

### 5. Motion Physics & Interactive Feedback

#### 5.1 Motion Engine Specifications
- **Spring Physics Standard:** `stiffness: 350`, `damping: 28`, `mass: 0.8` per Motion Division specification.
- **Transitions:** Easing cubic curve `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Micro-Interactions:** 150ms instantaneous feedback on hover and tap states.

#### 5.2 Judge Command Center Visual Indicators
- **Adaptive Debounce Ring:** Circular SVG ring animating backward from 8 seconds to 0 seconds when new messages arrive from a customer.
- **75s Counter SLA Gauge:** Visual countdown bar transitioning from Emerald (`#10B981`) to Amber (`#F59E0B`) at 45 seconds, pulsing Crimson (`#EF4444`) with soundbox trigger at 75 seconds.
- **Twin-Mode Indicator:** High-visibility toggle pill showing `[🟢 LIVE WHATSAPP CLOUD API]` vs `[⚡ DETERMINISTIC LOCAL REPLAY]`.
