import os
import json
import time
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
import httpx

class WordTimestamp(BaseModel):
    word: str
    start_time_ms: int
    end_time_ms: int
    confidence: float = 0.95

class STTResponse(BaseModel):
    transcript: str
    confidence: float = 0.95
    detected_language: str = "hi-IN"
    duration_sec: float = 0.0
    words: List[WordTimestamp] = Field(default_factory=list)
    is_fallback: bool = False
    raw_response: Optional[dict] = None

class GnaniSTTClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key or os.getenv("GNANI_API_KEY", "")
        self.base_url = (base_url or os.getenv("GNANI_API_BASE_URL", "https://api.vachana.ai")).rstrip("/")
        self.offline_mode = offline_mode
        self.fixtures_dir = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"

    def transcribe(
        self,
        audio_bytes: bytes,
        language_code: str = "hi-IN,en-IN",
        format_type: str = "codemix",
        keyterms: Optional[List[str]] = None,
        previous_text: Optional[str] = None,
        filename: str = "audio.ogg"
    ) -> STTResponse:
        """Transcribes audio payload via Gnani Prisma v3.0 REST endpoint or offline fixture."""
        if self.offline_mode or not self.api_key:
            return self._offline_fallback()

        url = f"{self.base_url}/stt/v3"
        headers = {"X-API-Key-ID": self.api_key}
        data = {
            "model": "prisma-v3.0",
            "language_code": language_code,
            "format": format_type,
        }
        if keyterms:
            data["keyterms"] = json.dumps(keyterms)
        if previous_text:
            data["previous_text"] = previous_text

        files = {"audio_file": (filename, audio_bytes, "application/octet-stream")}

        start_time = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, headers=headers, data=data, files=files)

        if res.status_code == 200:
            payload = res.json()
            return STTResponse(
                transcript=payload.get("transcript", ""),
                confidence=payload.get("confidence", 0.95),
                detected_language=payload.get("detected_language_code", "hi-IN"),
                duration_sec=round(time.perf_counter() - start_time, 2),
                is_fallback=False,
                raw_response=payload
            )
        else:
            # On error, raise or fallback
            raise RuntimeError(f"Gnani STT Error {res.status_code}: {res.text}")

    def _offline_fallback(self) -> STTResponse:
        """Returns deterministic fixture response for offline tests without burning credits."""
        cached_fixture = self.fixtures_dir / "smoke_test_results_redacted.json"
        if cached_fixture.exists():
            try:
                data = json.loads(cached_fixture.read_text(encoding="utf-8"))
                stt_data = data.get("results", {}).get("stt_whatsapp_note", {}).get("response", {})
                return STTResponse(
                    transcript=stt_data.get("transcript", "5kg Aashirvaad atta, pao bhar hari mirch, 10-wali 4 Maggi"),
                    confidence=0.96,
                    detected_language=stt_data.get("detected_language_code", "hi-IN"),
                    duration_sec=stt_data.get("end_to_end_latency", 1.2),
                    is_fallback=True
                )
            except Exception:
                pass

        return STTResponse(
            transcript="5kg Aashirvaad atta, pao bhar hari mirch, 10-wali 4 Maggi",
            confidence=0.95,
            detected_language="hi-IN",
            duration_sec=1.0,
            is_fallback=True
        )
