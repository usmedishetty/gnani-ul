# Agent Directives & Engineering Standards (Rules.md)
## Project GallaVaani: ASD-STE100 Compliance, Strict Invariants & Security Directives

---

### 1. Mandatory Operating Directives for AI Agents

1. **Spec-First Invariant:** AI coding agents must never write application code without first generating and validating all 8 specification files inside `.spec/`.
2. **Single Tool for Single Task Policy:** Always use the designated champion tool from the SYZYGY matrix. Do not introduce competing or redundant libraries.
3. **Deterministic Output:** Code must have complete type definitions, explicit error boundaries, and zero simulated fake data or unhandled exceptions.
4. **Zero-Drop Resilience:** Never drop a customer order due to ASR failure. Always trigger the 2-Strike Raw Audio Passthrough.

---

### 2. ASD-STE100 Technical English Rules

All documentation, logs, specifications, and system prompts must strictly obey **ASD-STE100** (Simplified Technical English):

#### 2.1 Banned Vocabulary (AI Slop & Marketing Filler)
The following words and phrases are strictly forbidden:
- `"game changer"`
- `"revolutionize"`
- `"delve"`
- `"testament"`
- `"cutting-edge"`
- `"seamlessly integrate"`
- `"transformative"`
- `"bespoke"`
- `"synergy"`
- `"holistic"`
- `"supercharge"`

#### 2.2 Structural Constraints
- Sentences must contain fewer than 25 words.
- Procedural instructions must contain fewer than 20 words.
- Use active voice with clear, unambiguous grammatical subjects.
- Maintain one specific meaning per technical term.
- Do not chain more than three noun modifiers (e.g., avoid "multi-tenant cloud microservice backend database architecture").

---

### 3. Hard Architectural Invariants

The following five invariants must be strictly enforced at the database level and within the state machine reducer:

#### Invariant 1: No Unverified Dispatch
- **Statement:** An order cannot transition to `CONFIRMED_PACKING` directly from `DRAFT_COLLECTING`.
- **Enforcement:** The state reducer requires a verified `merchant_approval_event_id` originating from the authenticated `shopkeeper_wa_id`.

#### Invariant 2: No Silent Upcharge
- **Statement:** If merchant revised total exceeds customer approved total by $>₹15$ or any line item brand changes, the system forbids transitioning to `CONFIRMED_PACKING` without intermediate customer consent.
- **Enforcement:** The order must route to `AWAITING_SUB_APPROVAL` and receive an explicit customer approval event.

#### Invariant 3: Monotonic Cart Version Locking
- **Statement:** Every cart mutation increments `cart_version_id`.
- **Enforcement:** Incoming interactive button clicks with `payload_version < current_cart_version` must be rejected as stale. The system prompts the user to interact with the latest message card.

#### Invariant 4: Idempotent Settlement
- **Statement:** An order in `DELIVERED_SETTLED` is financially immutable.
- **Enforcement:** Duplicate payment webhooks for the same `order_id` cannot trigger state changes. Excess funds automatically route to `EXCESS_PAYMENT_KHATA_CREDIT` on the customer ledger.

#### Invariant 5: Forbidden Post-Dispatch Self-Cancellation
- **Statement:** A customer cannot cancel an order once status transitions to `OUT_FOR_DELIVERY`.
- **Enforcement:** Customer webhooks with cancel actions in `OUT_FOR_DELIVERY` are blocked. Only `shopkeeper_wa_id` can authorize returns or cancellations once the delivery assistant departs.

---

### 4. Privacy, DPDP Act 2023 & Security Directives

#### 4.1 First-Touch DPDP Act 2023 Consent Notice
On the first interaction with any customer `wa_id`, the initial welcome card must display:
```text
🙏 Namaste! Yeh Sharma Store ka AI WhatsApp Sahayak hai. 
Aapke voice notes aur pata keval aapka order poora karne ke liye process kiye jaate hain. 
Voice clips 24 ghante mein auto-delete ho jaate hain.
```
- Users may send `STOP` or `DELETE DATA` at any time to purge their stored address, phone index, and audio history.

#### 4.2 Strict PII & Credential Scrubbing Guardrail
GallaVaani must never request, store, or log financial authentication credentials:
- **Prohibited Data:** UPI PINs, bank OTPs, credit/debit card numbers, CVVs, and government ID numbers (Aadhaar, PAN).
- **Pre-Logging Scrubber:** All incoming text and ASR transcripts pass through a regex scrubber before database insertion or LLM inference:
  ```python
  import re
  PII_SCRUB_REGEX = r'(?i)\b(?:pin|otp|cvv|password)\s*[:=]?\s*\d{4,6}\b|\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
  sanitized_text = re.sub(PII_SCRUB_REGEX, '[REDACTED_SENSITIVE_DIGITS]', raw_input)
  ```
- If credentials are detected, the system immediately transmits an advisory notice:
  *"⚠️ Suraksha ke liye WhatsApp par kabhi bhi apna UPI PIN, OTP ya Card number साझा na karein."*

#### 4.3 Cryptographically Scoped Voice Cloning Consent (`vachana-vc-v1`)
- Merchant voice embedding generation requires an enrollment audio sample reciting a verification challenge containing the merchant store name and current calendar date.
- The resulting `speaker_embedding` is bound to a hardened template service. The model can only speak pre-approved parameterized strings (e.g., `"Namaste {customer_name}, aapka order number {order_id} pack ho gaya hai"`). Arbitrary text synthesis is prohibited.

#### 4.4 24-Hour Ephemeral Audio Storage Policy
- Customer voice notes, cropped landmark clips, and passthrough audio files are stored in an encrypted S3/MinIO bucket.
- A hard lifecycle policy deletes all audio binaries exactly 24 hours after an order transitions to `DELIVERED_SETTLED`.
