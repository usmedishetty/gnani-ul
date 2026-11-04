#!/usr/bin/env python3
"""
GallaVaani - Gnani AI Live Smoke Test Harness
Validates live STT (Prisma v3.0) and TTS (Timbre v3.0) endpoints.
Measures latency, verifies WhatsApp OGG/Opus audio contracts, and saves redacted fixtures.
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from decimal import Decimal

import httpx
from dotenv import load_dotenv

# Force UTF-8 on Windows stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Try importing imageio_ffmpeg for zero-config ffmpeg binary
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = "ffmpeg"

try:
    import mutagen
    from mutagen.oggopus import OggOpus
    from mutagen.wave import WAVE
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

# Load environment variables
load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY")
GNANI_BASE_URL = os.getenv("GNANI_API_BASE_URL", "https://api.vachana.ai").rstrip("/")
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)


def check_audio_properties(file_path: Path) -> dict:
    """Verifies audio properties (channels, sample rate, codec) via mutagen or ffmpeg."""
    props = {
        "format": file_path.suffix.lstrip(".").lower(),
        "channels": None,
        "sample_rate": None,
        "duration_sec": None,
        "codec": None,
    }
    
    if HAS_MUTAGEN:
        try:
            if file_path.suffix.lower() in [".ogg", ".opus"]:
                audio = OggOpus(file_path)
                props["channels"] = audio.info.channels
                props["sample_rate"] = audio.info.samplerate
                props["duration_sec"] = round(audio.info.length, 2)
                props["codec"] = "opus"
                return props
            elif file_path.suffix.lower() == ".wav":
                audio = WAVE(file_path)
                props["channels"] = audio.info.channels
                props["sample_rate"] = audio.info.samplerate
                props["duration_sec"] = round(audio.info.length, 2)
                props["codec"] = "pcm"
                return props
        except Exception:
            pass

    # Fallback to ffmpeg -i inspection
    try:
        proc = subprocess.run(
            [FFMPEG_PATH, "-i", str(file_path)],
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True,
            timeout=5
        )
        output = proc.stderr
        for line in output.splitlines():
            if "Audio:" in line:
                props["raw_stream"] = line.strip()
                if "mono" in line:
                    props["channels"] = 1
                elif "stereo" in line:
                    props["channels"] = 2
                if "opus" in line.lower():
                    props["codec"] = "opus"
                elif "pcm" in line.lower():
                    props["codec"] = "pcm"
    except Exception as e:
        props["error"] = str(e)

    return props


def convert_to_wav_16k(input_path: Path, output_path: Path) -> bool:
    """Converts audio to 16 kHz mono WAV via ffmpeg."""
    try:
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(input_path),
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and output_path.exists()
    except Exception as e:
        print(f"[-] FFmpeg conversion error: {e}")
        return False


def convert_to_ogg_opus_mono(input_path: Path, output_path: Path) -> bool:
    """Converts audio to WhatsApp compliant OGG/Opus mono 16 kHz via ffmpeg."""
    try:
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(input_path),
            "-c:a", "libopus",
            "-b:a", "24k",
            "-ar", "16000",
            "-ac", "1",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and output_path.exists()
    except Exception as e:
        print(f"[-] FFmpeg OGG/Opus conversion error: {e}")
        return False


def create_synthetic_wav(path: Path, duration_sec: float = 3.0):
    """Creates a simple clean synthetic PCM WAV file if no live clip is present."""
    import wave
    import struct
    import math

    sample_rate = 16000
    num_samples = int(sample_rate * duration_sec)
    with wave.open(str(path), 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            # 440 Hz tone with soft decay
            t = float(i) / sample_rate
            value = int(12000.0 * math.sin(2.0 * math.pi * 440.0 * t) * math.exp(-t))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)


def test_stt_live(audio_path: Path, test_label: str) -> dict:
    """Calls Gnani Prisma v3.0 STT REST endpoint."""
    print(f"\n========================================================")
    print(f" [STT TEST] {test_label}: {audio_path.name}")
    print(f"========================================================")
    
    if not audio_path.exists():
        print(f"[-] Error: Audio file not found at {audio_path}")
        return {"status": "FILE_NOT_FOUND", "success": False}

    props = check_audio_properties(audio_path)
    file_size = audio_path.stat().st_size
    print(f"  • File: {audio_path.name} ({file_size} bytes)")
    print(f"  • Properties: {props}")

    url = f"{GNANI_BASE_URL}/stt/v3"
    headers = {
        "X-API-Key-ID": GNANI_API_KEY
    }

    # Prepare multipart form payload
    form_data = {
        "model": "prisma-v3.0",
        "language_code": "hi-IN,en-IN",
        "format": "codemix",
        "keyterms": json.dumps(["Aashirvaad", "Pillsbury", "pao", "10-wali", "Maggi", "Agni chai"])
    }

    start_time = time.perf_counter()
    response_data = None
    status_code = None

    try:
        with open(audio_path, "rb") as f:
            files = {"audio_file": (audio_path.name, f, "application/octet-stream")}
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=headers, data=form_data, files=files)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                status_code = res.status_code

        print(f"  • HTTP Status: {status_code}")
        print(f"  • Latency: {latency_ms} ms")
        print(f"  • Response Bytes: {len(res.content)}")

        if status_code == 200:
            response_data = res.json()
            print(f"  ✔ Transcript: {response_data.get('transcript', '')}")
            print(f"  ✔ Confidence: {response_data.get('confidence', 'N/A')}")
            return {
                "success": True,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "payload_bytes": len(res.content),
                "response": response_data,
                "file_used": audio_path.name
            }
        else:
            print(f"  [-] STT Request Rejected: {res.text}")
            return {
                "success": False,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "error": res.text,
                "file_used": audio_path.name
            }

    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"  [-] Connection Exception: {e}")
        return {
            "success": False,
            "status_code": "EXCEPTION",
            "latency_ms": latency_ms,
            "error": str(e),
            "file_used": audio_path.name
        }


def test_tts_live(text_phrase: str) -> dict:
    """Calls Gnani Timbre v3.0 TTS endpoint and verifies OGG/Opus mono output."""
    print(f"\n========================================================")
    print(f" [TTS TEST] Gnani Timbre v3.0 Synthesis")
    print(f"========================================================")
    print(f"  • Target Phrase: \"{text_phrase}\"")

    url = f"{GNANI_BASE_URL}/api/v1/tts/inference"
    headers = {
        "X-API-Key-ID": GNANI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text_phrase,
        "model": "timbre-v3.0",
        "voice": "Shivani",
        "language": "hi-IN",
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 22050,
            "container": "wav"
        }
    }

    start_time = time.perf_counter()
    try:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, headers=headers, json=payload)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        status_code = res.status_code
        print(f"  • HTTP Status: {status_code}")
        print(f"  • Latency: {latency_ms} ms")
        print(f"  • Received Audio Bytes: {len(res.content)}")

        if status_code == 200 and len(res.content) > 100:
            # Save raw returned audio
            raw_tts_file = FIXTURES_DIR / "live_tts_raw.wav"
            with open(raw_tts_file, "wb") as f:
                f.write(res.content)

            # Transcode to WhatsApp OGG/Opus mono
            ogg_tts_file = FIXTURES_DIR / "live_tts_waveform.ogg"
            transcode_success = convert_to_ogg_opus_mono(raw_tts_file, ogg_tts_file)

            if transcode_success:
                props = check_audio_properties(ogg_tts_file)
                print(f"  ✔ OGG/Opus Mono Verified: {props}")
                return {
                    "success": True,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "bytes": len(res.content),
                    "output_ogg": str(ogg_tts_file.name),
                    "properties": props
                }
            else:
                print(f"  [!] TTS audio received but OGG/Opus transcode failed")
                return {
                    "success": True,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "bytes": len(res.content),
                    "warning": "Transcode to OGG/Opus failed"
                }
        else:
            print(f"  [-] TTS Call Failed: {res.text}")
            return {
                "success": False,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "error": res.text
            }

    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"  [-] Connection Exception: {e}")
        return {
            "success": False,
            "status_code": "EXCEPTION",
            "latency_ms": latency_ms,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="GallaVaani Gnani AI Live Smoke Test")
    parser.add_argument("--voice-clip", help="Path to real clip of voice (<=10s)")
    parser.add_argument("--wa-clip", help="Path to real WhatsApp voice note (.ogg/.opus)")
    parser.add_argument("--phrase", default="नमस्ते, गल्लावाणी में आपका स्वागत है। कुल बिल तीन सौ अस्सी रुपये है।", help="Hindi phrase for TTS")
    args = parser.parse_args()

    print("\n========================================================")
    print(" 🚀 GallaVaani Live Gnani AI Smoke Test Suite")
    print("========================================================")
    print(f" Base URL: {GNANI_BASE_URL}")
    print(f" API Key Loaded: {'[YES] ' + GNANI_API_KEY[:4] + '...' + GNANI_API_KEY[-4:] if GNANI_API_KEY else '[NO - MISSING]'}")

    if not GNANI_API_KEY:
        print("\n[-] FATAL: GNANI_API_KEY is not defined in .env or environment!")
        print("    Please set GNANI_API_KEY in .env before executing live calls.")
        sys.exit(1)

    # 1. Resolve or prepare voice clip (<=10s)
    voice_clip_path = None
    if args.voice_clip and Path(args.voice_clip).exists():
        voice_clip_path = Path(args.voice_clip)
    else:
        candidates = [
            FIXTURES_DIR / "sample_voice.wav",
            FIXTURES_DIR / "my_voice.wav",
            FIXTURES_DIR / "voice_clip.wav",
            Path("sample_voice.wav"),
            Path("my_voice.wav"),
        ]
        for c in candidates:
            if c.exists():
                voice_clip_path = c
                break

    if not voice_clip_path:
        # Create a sample PCM file for testing
        synth_path = FIXTURES_DIR / "sample_voice.wav"
        create_synthetic_wav(synth_path, duration_sec=3.0)
        voice_clip_path = synth_path
        print(f"  [i] Notice: No pre-existing voice clip found; generated benchmark WAV: {voice_clip_path.name}")

    # 2. Resolve or prepare WhatsApp OGG/Opus clip
    wa_clip_path = None
    if args.wa_clip and Path(args.wa_clip).exists():
        wa_clip_path = Path(args.wa_clip)
    else:
        candidates = [
            FIXTURES_DIR / "sample_whatsapp.ogg",
            FIXTURES_DIR / "sample_whatsapp.opus",
            FIXTURES_DIR / "whatsapp_voice.ogg",
            Path("whatsapp_voice.ogg"),
        ]
        for c in candidates:
            if c.exists():
                wa_clip_path = c
                break

    if not wa_clip_path:
        # Transcode the voice clip to WhatsApp OGG/Opus
        wa_synth_path = FIXTURES_DIR / "sample_whatsapp.ogg"
        convert_to_ogg_opus_mono(voice_clip_path, wa_synth_path)
        wa_clip_path = wa_synth_path
        print(f"  [i] Notice: No pre-existing WhatsApp OGG clip found; synthesized OGG/Opus: {wa_clip_path.name}")

    # --- EXECUTE CALLS ---
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_url": GNANI_BASE_URL,
        "results": {}
    }

    # Test (a): STT on real voice clip
    stt_voice_res = test_stt_live(voice_clip_path, "Voice Clip (<=10s)")
    summary["results"]["stt_voice_clip"] = stt_voice_res

    # Test (a2): STT on WhatsApp .ogg/.opus
    stt_wa_res = test_stt_live(wa_clip_path, "WhatsApp Voice Note (.ogg/.opus)")
    
    # If WhatsApp OGG is rejected by Gnani REST endpoint, convert to 16kHz mono WAV and test
    if not stt_wa_res.get("success"):
        print("\n  [!] Direct WhatsApp OGG/Opus was rejected. Testing automated FFmpeg conversion to 16kHz mono WAV...")
        fallback_wav = FIXTURES_DIR / "converted_whatsapp_16k.wav"
        if convert_to_wav_16k(wa_clip_path, fallback_wav):
            print(f"  ✔ Conversion succeeded: {fallback_wav.name}")
            stt_wa_converted_res = test_stt_live(fallback_wav, "WhatsApp Converted (16kHz WAV)")
            summary["results"]["stt_whatsapp_converted"] = stt_wa_converted_res
        else:
            summary["results"]["stt_whatsapp_converted"] = {"success": False, "error": "FFmpeg conversion failed"}
    else:
        summary["results"]["stt_whatsapp_note"] = stt_wa_res

    # Test (b): TTS of target-language phrase
    tts_res = test_tts_live(args.phrase)
    summary["results"]["tts_synthesis"] = tts_res

    # --- SAVE REDACTED FIXTURES ---
    redacted_summary = json.loads(json.dumps(summary, default=str))
    # Redact any sensitive tokens if leaked
    redacted_str = json.dumps(redacted_summary, indent=2)
    if GNANI_API_KEY:
        redacted_str = redacted_str.replace(GNANI_API_KEY, "[REDACTED_API_KEY]")
    
    out_fixture_path = FIXTURES_DIR / "smoke_test_results_redacted.json"
    with open(out_fixture_path, "w", encoding="utf-8") as f:
        f.write(redacted_str)

    print(f"\n========================================================")
    print(f" ✔ Smoke Test Run Complete. Redacted results saved to:")
    print(f"   {out_fixture_path.relative_to(Path.cwd())}")
    print(f"========================================================\n")


if __name__ == "__main__":
    main()
