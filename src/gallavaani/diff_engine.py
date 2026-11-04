import re
from enum import Enum
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from gallavaani.fsm import CartItem, SKUKind

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
    diffs: List[ItemDiff] = Field(default_factory=list)
    net_price_delta: Decimal = Decimal("0.00")
    requires_customer_consent: bool = False
    final_total: Decimal = Decimal("0.00")
    ephemeral_oos_skus: List[str] = Field(default_factory=list)

class CartDiffEngine:
    def __init__(self):
        self.oos_cache: set[str] = set()

    def compute_diff(
        self,
        order_id: str,
        current_cart_version: int,
        current_items: List[CartItem],
        shopkeeper_transcript: str
    ) -> CartDiffResult:
        """Computes cart delta from shopkeeper voice override."""
        diffs: List[ItemDiff] = []
        updated_items = list(current_items)
        brand_swapped = False
        text = shopkeeper_transcript.lower()
        oos_items = []

        # Check for negation: "nahi hai" or "khatam"
        # Example: "Aashirvaad 5kg nahi hai Pillsbury hai 240 ka"
        if "nahi hai" in text or "khatam" in text:
            for idx, item in enumerate(current_items):
                item_name_lower = item.normalized_sku_name.lower()
                first_word = item_name_lower.split()[0]
                if first_word in text:
                    # Item is out of stock
                    oos_items.append(item.normalized_sku_name)
                    self.oos_cache.add(item.normalized_sku_name)

                    # Look for substitution brand e.g. "Pillsbury"
                    sub_match = re.search(r'([a-zA-Z\u0900-\u097F]+)\s+(?:hai|rakh\s+diya)\s*(?:₹\s*|rs\.?\s*)?(\d+)', text)
                    if sub_match:
                        sub_brand = sub_match.group(1).capitalize()
                        new_price = Decimal(sub_match.group(2))
                        
                        brand_swapped = True
                        new_item = CartItem(
                            line_index=item.line_index,
                            raw_spoken_text=sub_match.group(0),
                            normalized_sku_name=f"{sub_brand} {item.requested_quantity}{item.unit}",
                            kind=SKUKind.STANDARD_SKU,
                            requested_quantity=item.requested_quantity,
                            unit=item.unit,
                            unit_price=new_price,
                            line_total=new_price,
                            asr_confidence=0.96,
                            is_substituted=True,
                            substituted_from_sku=item.normalized_sku_name
                        )
                        diffs.append(ItemDiff(
                            action=SubstitutionAction.BRAND_SWAPPED,
                            original_item=item,
                            updated_item=new_item,
                            price_delta=new_price - item.line_total,
                            reason=f"Substituted {item.normalized_sku_name} with {sub_brand}"
                        ))
                        updated_items[idx] = new_item
                    else:
                        # Dropped without sub
                        diffs.append(ItemDiff(
                            action=SubstitutionAction.ITEM_REMOVED,
                            original_item=item,
                            price_delta=-item.line_total,
                            reason="Item Out of Stock"
                        ))
                        updated_items.remove(item)

        initial_total = sum((it.line_total for it in current_items), Decimal("0.00"))
        new_total = sum((it.line_total for it in updated_items), Decimal("0.00"))
        net_delta = new_total - initial_total

        # Invariant 2: price delta > Rs 15 or brand swap requires consent
        requires_consent = (net_delta > Decimal("15.00")) or brand_swapped

        return CartDiffResult(
            order_id=order_id,
            previous_cart_version=current_cart_version,
            new_cart_version=current_cart_version + 1,
            diffs=diffs,
            net_price_delta=net_delta,
            requires_customer_consent=requires_consent,
            final_total=new_total,
            ephemeral_oos_skus=oos_items
        )
