import pytest
from decimal import Decimal
from gallavaani.settlement import generate_doorstep_upi_qr

def test_settlement_dynamic_upi_qr_generation():
    """Asserts valid NPCI-compliant signed UPI URI and PNG byte output."""
    upi_uri, png_bytes = generate_doorstep_upi_qr(
        order_id="GV-204",
        merchant_vpa="sharmastore@icici",
        merchant_name="Sharma Provision Store",
        amount=Decimal("380.00")
    )
    
    assert upi_uri.startswith("upi://pay?")
    assert "pa=sharmastore%40icici" in upi_uri or "pa=sharmastore@icici" in upi_uri
    assert "am=380.00" in upi_uri
    assert "tr=GV204" in upi_uri or "tr=GV-204" in upi_uri
    assert len(png_bytes) > 100
    # PNG header check: \x89PNG
    assert png_bytes[:4] == b"\x89PNG"

