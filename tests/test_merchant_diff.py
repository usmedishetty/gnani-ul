import pytest
from decimal import Decimal
from gallavaani.diff_engine import CartDiffEngine, CartDiffResult
from gallavaani.fsm import CartItem, SKUKind

def test_diff_engine_item_swap_and_sub_approval():
    """Asserts 'Aashirvaad nahi hai Pillsbury 5kg hai 240 ka' swaps SKU and calculates net delta."""
    diff_engine = CartDiffEngine()
    current_items = [
        CartItem(
            line_index=1,
            raw_spoken_text="5kg Aashirvaad atta",
            normalized_sku_name="Aashirvaad Atta",
            kind=SKUKind.STANDARD_SKU,
            requested_quantity=Decimal("5.0"),
            unit="kg",
            unit_price=Decimal("255.00"),
            line_total=Decimal("255.00"),
            asr_confidence=0.95
        )
    ]
    
    shopkeeper_spoken_diff = "Aashirvaad 5kg nahi hai Pillsbury hai 240 ka"
    result = diff_engine.compute_diff(
        order_id="GV-204",
        current_cart_version=1,
        current_items=current_items,
        shopkeeper_transcript=shopkeeper_spoken_diff
    )
    
    assert isinstance(result, CartDiffResult)
    assert result.requires_customer_consent is True  # Brand swap requires customer consent
    assert any("pillsbury" in d.updated_item.normalized_sku_name.lower() for d in result.diffs if d.updated_item)
    assert result.final_total == Decimal("240.00")

