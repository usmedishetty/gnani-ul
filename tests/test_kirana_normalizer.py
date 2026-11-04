import pytest
from decimal import Decimal
from gallavaani.normalizer import KiranaNormalizer, CartIntentResult

def test_normalizer_colloquial_weights_pao_sawa_dhai():
    """Asserts Indian vernacular weights are deterministically normalized to SI units."""
    normalizer = KiranaNormalizer()
    
    # pao bhar = 0.25 kg / 250 g
    res1 = normalizer.normalize_text("pao bhar hari mirch")
    assert any(item.normalized_sku_name == "Hari Mirch" and item.requested_quantity == Decimal("0.25") and item.unit == "kg" for item in res1.items)

    # sawa kilo = 1.25 kg
    res2 = normalizer.normalize_text("sawa kilo tamatar")
    assert any(item.normalized_sku_name == "Tamatar" and item.requested_quantity == Decimal("1.25") and item.unit == "kg" for item in res2.items)

    # dhai sau gram = 0.25 kg
    res3 = normalizer.normalize_text("dhai sau gram adrak")
    assert any(item.requested_quantity == Decimal("0.25") for item in res3.items)

def test_normalizer_price_point_packs():
    """Asserts price-point pack syntax (e.g. 10-wali Maggi x4) is parsed."""
    normalizer = KiranaNormalizer()
    res = normalizer.normalize_text("10-wali 4 Maggi")
    
    maggi_items = [i for i in res.items if "maggi" in i.normalized_sku_name.lower()]
    assert len(maggi_items) == 1
    assert maggi_items[0].requested_quantity == Decimal("4")
    assert maggi_items[0].unit_price == Decimal("10.00")
    assert maggi_items[0].line_total == Decimal("40.00")

def test_normalizer_past_basket_resolution(mock_customer_history):
    """Asserts 'wahi pichli baar wali chai' resolves from customer history to 'Tata Tea Agni 250g'."""
    normalizer = KiranaNormalizer()
    res = normalizer.normalize_text(
        "ek kilo cheeni aur wahi pichli baar wali chai",
        customer_history=mock_customer_history
    )
    
    tea_items = [i for i in res.items if "tata tea" in i.normalized_sku_name.lower() or "agni" in i.normalized_sku_name.lower()]
    assert len(tea_items) == 1
    assert tea_items[0].requested_quantity == Decimal("0.25")
