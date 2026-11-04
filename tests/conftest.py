import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR

@pytest.fixture
def sample_voice_wav_bytes(fixtures_dir):
    wav_path = fixtures_dir / "my_voice.wav"
    if wav_path.exists():
        return wav_path.read_bytes()
    return b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

@pytest.fixture
def sample_whatsapp_ogg_bytes(fixtures_dir):
    ogg_path = fixtures_dir / "whatsapp_voice.ogg"
    if ogg_path.exists():
        return ogg_path.read_bytes()
    return b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00"

@pytest.fixture
def mock_customer_history():
    return [
        {
            "order_id": "GV-199",
            "items": [
                {"name": "Tata Tea Agni", "quantity": 0.25, "unit": "kg", "unit_price": 65.0, "total": 65.0},
                {"name": "Aashirvaad Atta", "quantity": 5.0, "unit": "kg", "unit_price": 255.0, "total": 255.0}
            ]
        }
    ]
