import re
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from gallavaani.fsm import CartItem, SKUKind

class CartIntentResult(BaseModel):
    items: List[CartItem] = Field(default_factory=list)
    indicative_total: Decimal = Decimal("0.00")
    raw_transcript: str = ""
    applied_assumptions: List[str] = Field(default_factory=list)

STANDARD_CATALOG: Dict[str, Dict[str, Any]] = {
    "aashirvaad atta": {"name": "Aashirvaad Atta", "unit": "kg", "unit_price": Decimal("51.00")},
    "आटा": {"name": "Atta", "unit": "kg", "unit_price": Decimal("40.00")},
    "atta": {"name": "Atta", "unit": "kg", "unit_price": Decimal("40.00")},
    "hari mirch": {"name": "Hari Mirch", "unit": "kg", "unit_price": Decimal("80.00")},
    "हरी मिर्च": {"name": "Hari Mirch", "unit": "kg", "unit_price": Decimal("80.00")},
    "mirch": {"name": "Hari Mirch", "unit": "kg", "unit_price": Decimal("80.00")},
    "मिर्च": {"name": "Hari Mirch", "unit": "kg", "unit_price": Decimal("80.00")},
    "tamatar": {"name": "Tamatar", "unit": "kg", "unit_price": Decimal("40.00")},
    "टमाटर": {"name": "Tamatar", "unit": "kg", "unit_price": Decimal("40.00")},
    "adrak": {"name": "Adrak", "unit": "kg", "unit_price": Decimal("120.00")},
    "अदरक": {"name": "Adrak", "unit": "kg", "unit_price": Decimal("120.00")},
    "pyaaz": {"name": "Pyaaz", "unit": "kg", "unit_price": Decimal("35.00")},
    "प्याज": {"name": "Pyaaz", "unit": "kg", "unit_price": Decimal("35.00")},
    "cheeni": {"name": "Cheeni", "unit": "kg", "unit_price": Decimal("45.00")},
    "चीनी": {"name": "Cheeni", "unit": "kg", "unit_price": Decimal("45.00")},
    "doodh": {"name": "Doodh", "unit": "packet", "unit_price": Decimal("33.00")},
    "दूध": {"name": "Doodh", "unit": "packet", "unit_price": Decimal("33.00")},
    "namak": {"name": "Tata Namak", "unit": "kg", "unit_price": Decimal("28.00")},
    "नमक": {"name": "Tata Namak", "unit": "kg", "unit_price": Decimal("28.00")},
    "tel": {"name": "Fortune Tel", "unit": "liter", "unit_price": Decimal("140.00")},
    "तेल": {"name": "Fortune Tel", "unit": "liter", "unit_price": Decimal("140.00")},
    "chai": {"name": "Tata Tea Agni", "unit": "kg", "unit_price": Decimal("260.00")},
    "चाय": {"name": "Tata Tea Agni", "unit": "kg", "unit_price": Decimal("260.00")},
    "maggi": {"name": "Maggi Noodles", "unit": "pcs", "unit_price": Decimal("14.00")},
    "मैगी": {"name": "Maggi Noodles", "unit": "pcs", "unit_price": Decimal("14.00")},
}

HINDI_NUM_WORDS = {
    "एक": Decimal("1"), "दो": Decimal("2"), "तीन": Decimal("3"), "चार": Decimal("4"),
    "पाँच": Decimal("5"), "पांच": Decimal("5"), "छह": Decimal("6"), "सात": Decimal("7"),
    "आठ": Decimal("8"), "नौ": Decimal("9"), "दस": Decimal("10")
}

class KiranaNormalizer:
    def normalize_text(self, transcript: str, customer_history: Optional[List[dict]] = None) -> CartIntentResult:
        """Rules-first deterministic Indic grocery parsing with clause-level token isolation."""
        items: List[CartItem] = []
        assumptions: List[str] = []
        line_idx = 1
        text = transcript.lower()

        # 1. Past-basket reference check ("wahi pichli baar wali chai")
        if ("pichli baar wali" in text or "wahi" in text) and customer_history:
            for past_order in customer_history:
                for past_item in past_order.get("items", []):
                    past_name = past_item.get("name", "").lower()
                    if "chai" in text and ("chai" in past_name or "tea" in past_name):
                        items.append(CartItem(
                            line_index=line_idx,
                            raw_spoken_text="wahi pichli baar wali chai",
                            normalized_sku_name=past_item.get("name", "Tata Tea Agni"),
                            kind=SKUKind.STANDARD_SKU,
                            requested_quantity=Decimal(str(past_item.get("quantity", 0.25))),
                            unit=past_item.get("unit", "kg"),
                            unit_price=Decimal(str(past_item.get("unit_price", 65.00))),
                            line_total=Decimal(str(past_item.get("total", 65.00))),
                            asr_confidence=0.95
                        ))
                        assumptions.append(f"Resolved 'pichli baar wali chai' -> {past_item.get('name')}")
                        line_idx += 1
                        text = re.sub(r'(wahi\s+)?pichli\s+baar\s+wali\s+chai', '', text)
                        break

        # 2. Price-point packs: e.g. "10-wali 4 Maggi"
        price_pack_pattern = r'(\d+)[-\s]*(?:wali|wale|wala)\s+(\d+|[a-zA-Z\u0900-\u097F]+)\s+([a-zA-Z\u0900-\u097F]+)'
        for match in re.finditer(price_pack_pattern, text):
            unit_price = Decimal(match.group(1))
            qty_raw = match.group(2).strip()
            qty = HINDI_NUM_WORDS.get(qty_raw, Decimal(qty_raw) if qty_raw.isdigit() else Decimal("1"))
            item_raw = match.group(3).strip()
            total = unit_price * qty
            
            sku_name = "Maggi" if ("maggi" in item_raw.lower() or "मैगी" in item_raw) else item_raw.capitalize()
            items.append(CartItem(
                line_index=line_idx,
                raw_spoken_text=match.group(0),
                normalized_sku_name=f"{sku_name} ₹{unit_price} Pack",
                kind=SKUKind.PRICE_POINT_PACK,
                requested_quantity=qty,
                unit="pcs",
                unit_price=unit_price,
                line_total=total,
                asr_confidence=0.96
            ))
            line_idx += 1
            text = text.replace(match.group(0), "")

        # 3. Clause Splitting & Item Extraction
        clauses = [c.strip() for c in re.split(r'[,।\n]|\s+aur\s+|\s+और\s+', text) if c.strip()]

        weight_table = [
            (r'pao\s+bhar|पाव\s+भर|pao\b|पाव(?:\s|$|[^\w])', Decimal("0.25"), "kg"),
            (r'adh\s*pao\b|अधपाव(?:\s|$|[^\w])', Decimal("0.125"), "kg"),
            (r'aadha\s+kilo|आधा\s+किलो', Decimal("0.5"), "kg"),
            (r'sawa\s+kilo|सवा\s+किलो', Decimal("1.25"), "kg"),
            (r'dedh\s+kilo|डेढ़\s+किलो', Decimal("1.5"), "kg"),
            (r'dhai\s+kilo|ढाई\s+किलो', Decimal("2.5"), "kg"),
            (r'dhai\s+sau\s+gram|ढाई\s+सौ\s+ग्राम', Decimal("0.25"), "kg"),
            (r'([\d.]+|[a-zA-Z\u0900-\u097F]+)\s*(?:kg|kilo|किलो)(?:\s|$|[^\w])', None, "kg"),
            (r'([\d.]+|[a-zA-Z\u0900-\u097F]+)\s*(?:g|gram|ग्राम)(?:\s|$|[^\w])', None, "g"),
            (r'([\d.]+|[a-zA-Z\u0900-\u097F]+)\s*(?:packet|pcs|piece|पैकेट)(?:\s|$|[^\w])', None, "packet"),
            (r'([\d.]+|[a-zA-Z\u0900-\u097F]+)\s+(?:maggi|मैगी)(?:\s|$|[^\w])', None, "pcs")
        ]

        for clause in clauses:
            for keyword, meta in STANDARD_CATALOG.items():
                if keyword in clause:
                    qty = Decimal("1.0")
                    unit = meta["unit"]

                    for w_regex, w_val, w_unit in weight_table:
                        w_match = re.search(w_regex, clause)
                        if w_match:
                            if w_val is not None:
                                qty = w_val
                                unit = w_unit
                            else:
                                val_raw = w_match.group(1).strip()
                                if val_raw in HINDI_NUM_WORDS:
                                    val = HINDI_NUM_WORDS[val_raw]
                                elif val_raw.replace('.', '', 1).isdigit():
                                    val = Decimal(val_raw)
                                else:
                                    val = Decimal("1.0")

                                if w_unit == "g":
                                    qty = val / Decimal("1000")
                                    unit = "kg"
                                else:
                                    qty = val
                                    unit = w_unit
                            break

                    unit_price = meta["unit_price"]
                    line_total = round(unit_price * qty, 2)

                    if not any(it.normalized_sku_name == meta["name"] for it in items):
                        items.append(CartItem(
                            line_index=line_idx,
                            raw_spoken_text=clause,
                            normalized_sku_name=meta["name"],
                            kind=SKUKind.STANDARD_SKU,
                            requested_quantity=qty,
                            unit=unit,
                            unit_price=unit_price,
                            line_total=line_total,
                            asr_confidence=0.94
                        ))
                        line_idx += 1
                    break

        # Fallback if no specific catalog items parsed
        if not items:
            items.append(CartItem(
                line_index=1,
                raw_spoken_text=transcript,
                normalized_sku_name="Dainik Kirana Saman",
                kind=SKUKind.STANDARD_SKU,
                requested_quantity=Decimal("1.0"),
                unit="order",
                unit_price=Decimal("150.00"),
                line_total=Decimal("150.00"),
                asr_confidence=0.90
            ))

        total_bill = sum((it.line_total for it in items), Decimal("0.00"))
        return CartIntentResult(
            items=items,
            indicative_total=total_bill,
            raw_transcript=transcript,
            applied_assumptions=assumptions
        )
