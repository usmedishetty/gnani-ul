import os
import sys
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv

from gallavaani.pipeline import GallaVaaniPipeline

# Force UTF-8 on Windows stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="GallaVaani Voice-Note Intake CLI")
    parser.add_argument("audio", help="Path to input audio file (WAV, OGG, Opus, AAC)")
    parser.add_argument("--live", action="store_true", help="Execute live calls against api.vachana.ai (requires GNANI_API_KEY in .env)")
    parser.add_argument("--lang", default="hi-IN,en-IN", help="Language code hint (default: hi-IN,en-IN)")
    parser.add_argument("--store", default="Sharma Store", help="Merchant store name")
    parser.add_argument("--order-id", default="GV-204", help="Order identifier")
    parser.add_argument("--out-audio", default="tests/fixtures/output_reply.ogg", help="Path to save synthesized readback OGG audio")

    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"[-] Error: Input audio file not found: {audio_path}")
        sys.exit(1)

    audio_bytes = audio_path.read_bytes()
    offline_mode = not args.live

    print("\n" + "=" * 65)
    print(" 🎙️  GALLAVAANI VOICE COMMERCE INTAKE PIPELINE")
    print("=" * 65)
    print(f" Input File : {audio_path.name} ({len(audio_bytes):,} bytes)")
    print(f" Execution  : {'🟢 LIVE GNANI API' if args.live else '⚡ OFFLINE / ZERO-CREDIT FIXTURE'}")
    print(f" Language   : {args.lang}")
    print(f" Store Name : {args.store}")
    print("=" * 65)

    pipeline = GallaVaaniPipeline(offline_mode=offline_mode)

    try:
        res = pipeline.run(
            audio_bytes=audio_bytes,
            language_hint=args.lang,
            order_id=args.order_id,
            store_name=args.store,
            filename=audio_path.name
        )
    except Exception as e:
        print(f"\n[-] Pipeline Failure: {e}")
        sys.exit(1)

    timings = res["timings"]

    # STEP 1: STT
    print(f"\n[Step 1: STT Ingestion & Denoising] ➔ ✔ OK ({timings['stt_ms']:.1f} ms)")
    print(f"  Transcript: \"{res['transcript']}\"")

    # STEP 2: Intent & Normalization
    intent = res["intent_result"]
    print(f"\n[Step 2: Kirana Normalizer & FSM]  ➔ ✔ OK ({timings['norm_ms']:.1f} ms)")
    for it in intent["items"]:
        print(f"  • {it['line_index']}. {it['normalized_sku_name']} ({it['requested_quantity']} {it['unit']}) @ ₹{it['unit_price']} = ₹{it['line_total']:.2f}")
    print(f"  💰 Indicative Total: ₹{intent['indicative_total']}")

    # STEP 3: Presentation Parchi
    print(f"\n[Step 3: Response Parchi Formatter]➔ ✔ OK ({timings['parchi_ms']:.1f} ms)")
    card_preview = "\n".join("    " + line for line in res["reply_text"].splitlines()[:6])
    print(f"{card_preview}\n    ...")

    # STEP 4: TTS & OGG/Opus Waveform
    out_audio_path = Path(args.out_audio)
    out_audio_path.parent.mkdir(parents=True, exist_ok=True)
    out_audio_path.write_bytes(res["reply_audio_bytes"])

    print(f"\n[Step 4: TTS Readback Synthesis]   ➔ ✔ OK ({timings['tts_ms']:.1f} ms)")
    print(f"  Audio Output: {out_audio_path} ({len(res['reply_audio_bytes']):,} bytes, OGG/Opus mono)")

    print("\n" + "=" * 65)
    print(f" ✔ PIPELINE FINISHED IN {timings['total_ms']:.1f} ms (Target SLA < 2800 ms)")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
