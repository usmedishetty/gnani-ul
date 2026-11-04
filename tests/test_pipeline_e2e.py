import pytest
from gallavaani.pipeline import GallaVaaniPipeline

def test_pipeline_run_end_to_end_offline(sample_voice_wav_bytes):
    """Asserts pipeline.run executes the 4-stage pipeline offline returning the required dictionary schema."""
    pipeline = GallaVaaniPipeline(offline_mode=True)
    result = pipeline.run(audio_bytes=sample_voice_wav_bytes, language_hint="hi-IN")
    
    # Contract validation: {transcript, intent_result, reply_text, reply_audio_bytes, timings}
    assert "transcript" in result
    assert "intent_result" in result
    assert "reply_text" in result
    assert "reply_audio_bytes" in result
    assert "timings" in result

    # Check timings has per-step breakdown
    timings = result["timings"]
    assert "stt_ms" in timings
    assert "norm_ms" in timings
    assert "parchi_ms" in timings
    assert "tts_ms" in timings
    assert "total_ms" in timings

    # Check reply audio is OGG/Opus
    assert len(result["reply_audio_bytes"]) > 0
    assert result["reply_audio_bytes"][:4] == b"OggS"

    # Check reply text has WhatsApp formatting
    assert "Sharma Store" in result["reply_text"] or "Parchi" in result["reply_text"]
