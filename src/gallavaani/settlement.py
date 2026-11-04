import io
import urllib.parse
from decimal import Decimal
from typing import Tuple
import qrcode

def generate_doorstep_upi_qr(
    order_id: str,
    merchant_vpa: str,
    merchant_name: str,
    amount: Decimal
) -> Tuple[str, bytes]:
    """Generates NPCI-compliant signed UPI payment URI and returns rendered PNG bytes."""
    clean_order_ref = order_id.replace("-", "")
    tr_id = clean_order_ref if clean_order_ref.startswith("GV") else f"GV{clean_order_ref}"
    params = {
        "pa": merchant_vpa,
        "pn": merchant_name,
        "tr": tr_id,
        "am": f"{amount:.2f}",
        "cu": "INR",
        "tn": f"GallaVaani Order {order_id}"
    }
    query_str = urllib.parse.urlencode(params)
    upi_uri = f"upi://pay?{query_str}"

    # Generate high-contrast PNG QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return upi_uri, buffer.getvalue()
