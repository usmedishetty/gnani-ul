import pytest
from decimal import Decimal
from gallavaani.fsm import OrderFSM, OrderStatus, InvariantViolationError, CartItem, OrderCart

def test_fsm_invariant_1_prevent_unverified_dispatch():
    """Invariant 1: An order cannot transition to CONFIRMED_PACKING without authentic merchant approval."""
    fsm = OrderFSM(order_id="GV-204")
    assert fsm.status == OrderStatus.DRAFT_COLLECTING
    
    # Attempting direct transition to CONFIRMED_PACKING without approval event must raise InvariantViolationError
    with pytest.raises(InvariantViolationError) as exc:
        fsm.transition_to(OrderStatus.CONFIRMED_PACKING, actor_role="customer")
    assert "Invariant 1" in str(exc.value)

def test_fsm_invariant_2_silent_upcharge_protection():
    """Invariant 2: Price increase > Rs 15 or brand swap forces state to AWAITING_SUB_APPROVAL."""
    fsm = OrderFSM(order_id="GV-204")
    fsm.cart.indicative_total = Decimal("300.00")
    fsm.status = OrderStatus.AWAITING_SHOP_APPROVAL
    
    # Merchant proposes Rs 320 (+20 > 15)
    fsm.apply_merchant_diff(new_total=Decimal("320.00"), brand_swapped=False)
    assert fsm.status == OrderStatus.AWAITING_SUB_APPROVAL

def test_fsm_invariant_3_stale_cart_version_rejected():
    """Invariant 3: Actions on stale cart version IDs must be rejected."""
    fsm = OrderFSM(order_id="GV-204")
    assert fsm.cart_version_id == 1
    
    # Mutating cart increments version
    fsm.mutate_cart(items=[])
    assert fsm.cart_version_id == 2
    
    # Action with old version payload must fail
    with pytest.raises(InvariantViolationError) as exc:
        fsm.confirm_by_customer(payload_version=1)
    assert "Invariant 3" in str(exc.value)
