import pytest
from gallavaani.tts import GnaniTTSClient, TTSResponse, expand_indic_numbers

def test_tts_indic_number_expansion():
    """Asserts numbers and currency are phonetically expanded for natural Indic speech."""
    expanded1 = expand_indic_numbers("कुल बिल ₹450 है।")
    assert "चार सौ पचास रुपये" in expanded1 or "chaar sau pachaas" in expanded1.lower()

    expanded2 = expand_indic_numbers("पर्ची #204")
    assert "दो सौ चार" in expanded2 or "do sau chaar" in expanded2.lower()

def test_tts_offline_synthesis_returns_ogg_opus():
    """Asserts TTS client returns WhatsApp compliant OGG/Opus audio bytes in offline fixture mode."""
    tts_client = GnaniTTSClient(api_key="mock_key", offline_mode=True)
    res = tts_client.synthesize("नमस्ते, आपका आर्डर दर्ज हो गया है।", voice="Shivani")
    
    assert isinstance(res, TTSResponse)
    assert len(res.audio_bytes) > 0
    assert res.output_format == "audio/ogg; codecs=opus"
    # Verify Ogg header signature 'OggS'
    assert res.audio_bytes[:4] == b"OggS"

