from enum import Enum
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class OrderStatus(str, Enum):
    DRAFT_COLLECTING = "DRAFT_COLLECTING"
    DRAFT_PAUSED = "DRAFT_PAUSED"
    AWAITING_SHOP_APPROVAL = "AWAITING_SHOP_APPROVAL"
    AWAITING_SUB_APPROVAL = "AWAITING_SUB_APPROVAL"
    CONFIRMED_PACKING = "CONFIRMED_PACKING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED_SETTLED = "DELIVERED_SETTLED"
    CANCELLED = "CANCELLED"

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
    asr_confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    audio_slice_path: Optional[str] = None
    is_substituted: bool = False
    substituted_from_sku: Optional[str] = None

class OrderCart(BaseModel):
    order_id: str
    cart_version_id: int = 1
    items: List[CartItem] = Field(default_factory=list)
    indicative_total: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    final_total: Optional[Decimal] = None

class InvariantViolationError(Exception):
    """Raised when an operation violates any of the 5 canonical architectural invariants."""
    pass

class OrderFSM:
    def __init__(self, order_id: str, customer_wa_id: str = "+919800000000"):
        self.order_id = order_id
        self.customer_wa_id = customer_wa_id
        self.cart_version_id = 1
        self.status = OrderStatus.DRAFT_COLLECTING
        self.cart = OrderCart(order_id=order_id, cart_version_id=self.cart_version_id)
        self.merchant_approval_event_id: Optional[str] = None

    def mutate_cart(self, items: List[CartItem]):
        """Mutates items in cart, incrementing cart_version_id monotonically (Invariant 3)."""
        self.cart_version_id += 1
        self.cart.cart_version_id = self.cart_version_id
        self.cart.items = items
        self.cart.indicative_total = sum((item.line_total for item in items), Decimal("0.00"))

    def confirm_by_customer(self, payload_version: int):
        """Customer taps [Pakka Karo] on interactive parchi."""
        if payload_version != self.cart_version_id:
            raise InvariantViolationError(
                f"Invariant 3 Violation: Monotonic version lock mismatch (payload v{payload_version} != current v{self.cart_version_id})"
            )
        self.status = OrderStatus.AWAITING_SHOP_APPROVAL

    def apply_merchant_diff(self, new_total: Decimal, brand_swapped: bool):
        """Applies merchant voice diff enforcing silent upcharge threshold (Invariant 2)."""
        delta = new_total - self.cart.indicative_total
        self.cart.final_total = new_total

        # Invariant 2: If price delta > Rs 15 or brand swap occurred, require customer sub approval
        if delta > Decimal("15.00") or brand_swapped:
            self.status = OrderStatus.AWAITING_SUB_APPROVAL
        else:
            self.status = OrderStatus.CONFIRMED_PACKING

    def transition_to(self, target_status: OrderStatus, actor_role: Literal["customer", "merchant", "system"]):
        """Deterministic state transition validator enforcing Invariants 1, 4, 5."""
        # Invariant 4: Financial state in DELIVERED_SETTLED is immutable
        if self.status == OrderStatus.DELIVERED_SETTLED:
            raise InvariantViolationError("Invariant 4 Violation: Order is settled and immutable.")

        # Invariant 5: Customer cannot cancel after OUT_FOR_DELIVERY
        if self.status == OrderStatus.OUT_FOR_DELIVERY and target_status == OrderStatus.CANCELLED:
            if actor_role == "customer":
                raise InvariantViolationError("Invariant 5 Violation: Forbidden post-dispatch self-cancellation by customer.")

        # Invariant 1: No Unverified Dispatch without merchant approval
        if target_status == OrderStatus.CONFIRMED_PACKING:
            if not self.merchant_approval_event_id and actor_role != "merchant":
                raise InvariantViolationError("Invariant 1 Violation: Cannot transition to CONFIRMED_PACKING without verified merchant approval.")

        self.status = target_status
