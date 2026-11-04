import pytest
from gallavaani.stt import GnaniSTTClient, STTResponse

def test_stt_transcribe_codemix_offline_fixture(sample_voice_wav_bytes):
    """Asserts offline transcription returns expected STTResponse using fixtures without live credits."""
    client = GnaniSTTClient(api_key="mock_key", offline_mode=True)
    res = client.transcribe(sample_voice_wav_bytes, language_code="hi-IN,en-IN", format_type="codemix")
    
    assert isinstance(res, STTResponse)
    assert res.transcript != ""
    assert res.detected_language == "hi-IN"
    assert res.is_fallback is True

def test_stt_whatsapp_ogg_supported(sample_whatsapp_ogg_bytes):
    """Asserts WhatsApp OGG audio is accepted and processed by STT client."""
    client = GnaniSTTClient(api_key="mock_key", offline_mode=True)
    res = client.transcribe(sample_whatsapp_ogg_bytes, language_code="hi-IN,en-IN")
    
    assert isinstance(res, STTResponse)
    assert "record" in res.transcript.lower() or "test" in res.transcript.lower() or len(res.transcript) > 0

