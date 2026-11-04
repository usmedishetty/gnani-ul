from decimal import Decimal
from typing import List, Dict, Any
from gallavaani.fsm import CartItem, OrderCart
from gallavaani.tts import number_to_hindi

class ParchiFormatter:
    @staticmethod
    def format_customer_parchi(
        cart: OrderCart,
        store_name: str = "Sharma Store",
        customer_address: str = "Mohalla Central, Kanpur",
        payment_mode: str = "Doorstep UPI QR / Cash"
    ) -> Dict[str, Any]:
        """Formats WhatsApp high-contrast text card and spoken Hindi script for Timbre readback."""
        lines = [
            f"🧾 *{store_name} - Kacchi Parchi #{cart.order_id}*",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]

        for item in cart.items:
            unit_str = f"({item.requested_quantity} {item.unit})"
            lines.append(f"{item.line_index}. *{item.normalized_sku_name}* {unit_str} — ₹{item.line_total:.2f}")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"💰 *Andazan Bill: ~₹{cart.indicative_total:.2f}*",
            f"📍 *Pata:* {customer_address}",
            f"💳 *Mode:* {payment_mode}",
            "",
            "_Stock confirm hone par dukandar pakka bill bhejenge._"
        ])

        card_text = "\n".join(lines)

        # Generate phonetic Indic spoken readback script for TTS
        item_count = len(cart.items)
        hindi_count = number_to_hindi(item_count)
        hindi_total = number_to_hindi(int(cart.indicative_total))
        spoken_script = f"कुल {hindi_count} आइटम। अंदाज़न बिल {hindi_total} रुपये। {store_name} से आपकी कच्ची पर्ची तैयार है।"

        return {
            "order_id": cart.order_id,
            "card_text": card_text,
            "spoken_script_hindi": spoken_script,
            "buttons": [
                {"id": f"CONFIRM_{cart.order_id}_V{cart.cart_version_id}", "title": "✅ Pakka Karo"},
                {"id": f"MUTATE_{cart.order_id}_V{cart.cart_version_id}", "title": "🎙️ Badlo / Jodo"},
                {"id": f"PAY_{cart.order_id}_V{cart.cart_version_id}", "title": "💳 Mode"}
            ]
        }

