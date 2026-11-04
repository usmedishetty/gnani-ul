import os
import re
import time
import subprocess
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import httpx

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = "ffmpeg"

class TTSResponse(BaseModel):
    audio_bytes: bytes
    output_format: str = "audio/ogg; codecs=opus"
    duration_sec: float = 0.0
    voice_used: str = "Shivani"
    is_fallback: bool = False

HINDI_NUMBERS = {
    0: "शून्य", 1: "एक", 2: "दो", 3: "तीन", 4: "चार", 5: "पांच",
    6: "छह", 7: "सात", 8: "आठ", 9: "नौ", 10: "दस",
    11: "ग्यारह", 12: "बारह", 13: "तेरह", 14: "चौदह", 15: "पंद्रह",
    16: "सोलह", 17: "सत्रह", 18: "अठारह", 19: "उन्नीस", 20: "बीस",
    25: "पच्चीस", 30: "तीस", 35: "पैंतीस", 40: "चालीस", 45: "पैंतालीस",
    50: "पचास", 60: "साठ", 70: "सत्तर", 80: "अस्सी", 90: "नब्बे",
    100: "सौ", 200: "दो सौ", 204: "दो सौ चार", 300: "तीन सौ",
    380: "तीन सौ अस्सी", 400: "चार सौ", 450: "चार सौ पचास", 500: "पांच सौ"
}

def number_to_hindi(num: int) -> str:
    """Converts integers up to 999 into Hindi words."""
    if num in HINDI_NUMBERS:
        return HINDI_NUMBERS[num]
    if num < 100:
        tens = (num // 10) * 10
        rem = num % 10
        return f"{HINDI_NUMBERS.get(tens, '')} {HINDI_NUMBERS.get(rem, '')}".strip()
    if num < 1000:
        hundreds = num // 100
        rem = num % 100
        h_str = f"{HINDI_NUMBERS.get(hundreds, '')} सौ"
        if rem == 0:
            return h_str
        return f"{h_str} {number_to_hindi(rem)}".strip()
    return str(num)

def expand_indic_numbers(text: str) -> str:
    """Expands currency symbols and numbers into phonetic Hindi text."""
    # 1. Expand currency: ₹450 / Rs 450 / 450 rs -> चार सौ पचास रुपये
    def replace_currency(match):
        val = int(match.group(1))
        return f"{number_to_hindi(val)} रुपये"

    expanded = re.sub(r'(?:₹|rs\.?)\s*(\d+)', replace_currency, text, flags=re.IGNORECASE)
    expanded = re.sub(r'(\d+)\s*(?:rupaye|rupees|rs)', replace_currency, expanded, flags=re.IGNORECASE)

    # 2. Expand order numbers: #204 -> पर्ची नंबर दो सौ चार
    def replace_order_id(match):
        val = int(match.group(1))
        return f"पर्ची नंबर {number_to_hindi(val)}"

    expanded = re.sub(r'#(?:gv-?)?(\d+)', replace_order_id, expanded, flags=re.IGNORECASE)

    return expanded

class GnaniTTSClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, offline_mode: bool = False):
        self.api_key = api_key or os.getenv("GNANI_API_KEY", "")
        self.base_url = (base_url or os.getenv("GNANI_API_BASE_URL", "https://api.vachana.ai")).rstrip("/")
        self.offline_mode = offline_mode
        self.fixtures_dir = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"

    def synthesize(self, text: str, voice: str = "Shivani", speed: float = 1.0) -> TTSResponse:
        """Synthesizes text and transcodes to WhatsApp-compliant OGG/Opus mono."""
        expanded_text = expand_indic_numbers(text)

        if self.offline_mode or not self.api_key:
            return self._offline_fallback()

        url = f"{self.base_url}/api/v1/tts/inference"
        headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": expanded_text,
            "model": "timbre-v3.0",
            "voice": voice,
            "language": "hi-IN",
            "speed": speed,
            "audio_config": {
                "sample_rate": 22050,
                "container": "wav"
            }
        }

        start_time = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, headers=headers, json=payload)

        if res.status_code == 200 and len(res.content) > 100:
            duration = round(time.perf_counter() - start_time, 2)
            # Transcode returned WAV bytes to OGG/Opus mono
            ogg_bytes = self._transcode_to_ogg_opus(res.content)
            return TTSResponse(
                audio_bytes=ogg_bytes,
                output_format="audio/ogg; codecs=opus",
                duration_sec=duration,
                voice_used=voice,
                is_fallback=False
            )
        else:
            raise RuntimeError(f"Gnani TTS Error {res.status_code}: {res.text}")

    def _transcode_to_ogg_opus(self, wav_bytes: bytes) -> bytes:
        """Transcodes WAV bytes to 16kHz mono OGG/Opus via FFmpeg pipe."""
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", "pipe:0",
            "-c:a", "libopus",
            "-b:a", "24k",
            "-ar", "16000",
            "-ac", "1",
            "-f", "ogg",
            "pipe:1"
        ]
        proc = subprocess.run(cmd, input=wav_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return proc.stdout

    def _offline_fallback(self) -> TTSResponse:
        """Loads cached OGG/Opus waveform fixture for zero-credit testing."""
        cached_ogg = self.fixtures_dir / "live_tts_waveform.ogg"
        if cached_ogg.exists():
            return TTSResponse(
                audio_bytes=cached_ogg.read_bytes(),
                output_format="audio/ogg; codecs=opus",
                duration_sec=1.5,
                voice_used="Shivani",
                is_fallback=True
            )

        # Generate minimal OGG dummy header
        return TTSResponse(
            audio_bytes=b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01\x13OpusHead\x01\x01\x00\x00\x80>\x00\x00\x00\x00\x00",
            output_format="audio/ogg; codecs=opus",
            duration_sec=1.0,
            voice_used="Shivani",
            is_fallback=True
        )

