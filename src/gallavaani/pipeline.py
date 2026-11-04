import time
from decimal import Decimal
from typing import Optional, Dict, Any, List
from gallavaani.stt import GnaniSTTClient
from gallavaani.normalizer import KiranaNormalizer
from gallavaani.fsm import OrderFSM, OrderCart
from gallavaani.parchi import ParchiFormatter
from gallavaani.tts import GnaniTTSClient

class GallaVaaniPipeline:
    def __init__(self, offline_mode: bool = False, api_key: Optional[str] = None):
        self.offline_mode = offline_mode
        self.stt_client = GnaniSTTClient(api_key=api_key, offline_mode=offline_mode)
        self.normalizer = KiranaNormalizer()
        self.tts_client = GnaniTTSClient(api_key=api_key, offline_mode=offline_mode)

    def run(
        self,
        audio_bytes: bytes,
        language_hint: str = "hi-IN",
        order_id: str = "GV-204",
        customer_history: Optional[List[dict]] = None,
        store_name: str = "Sharma Store",
        filename: str = "input.ogg"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end voice-note intake pipeline:
        audio bytes -> transcript -> intent result -> reply text -> reply audio bytes
        Returns {transcript, intent_result, reply_text, reply_audio_bytes, timings}.
        """
        start_pipeline = time.perf_counter()

        # Step 1: Speech-to-Text (Gnani Prisma v3.0 REST)
        t0 = time.perf_counter()
        stt_res = self.stt_client.transcribe(
            audio_bytes=audio_bytes,
            language_code=language_hint,
            format_type="codemix",
            keyterms=["Aashirvaad", "Pillsbury", "pao", "10-wali", "Maggi", "Agni chai"],
            filename=filename
        )
        stt_ms = round((time.perf_counter() - t0) * 1000, 2)

        # Step 2: Kirana Intent & Normalization (Rules-First)
        t1 = time.perf_counter()
        intent_res = self.normalizer.normalize_text(
            transcript=stt_res.transcript,
            customer_history=customer_history
        )
        norm_ms = round((time.perf_counter() - t1) * 1000, 2)

        # Step 3: FSM State & Parchi Formatting
        t2 = time.perf_counter()
        fsm = OrderFSM(order_id=order_id)
        fsm.mutate_cart(intent_res.items)
        parchi_data = ParchiFormatter.format_customer_parchi(
            cart=fsm.cart,
            store_name=store_name
        )
        parchi_ms = round((time.perf_counter() - t2) * 1000, 2)

        # Step 4: Text-to-Speech (Gnani Timbre v3.0 OGG/Opus Mono)
        t3 = time.perf_counter()
        tts_res = self.tts_client.synthesize(
            text=parchi_data["spoken_script_hindi"],
            voice="Shivani"
        )
        tts_ms = round((time.perf_counter() - t3) * 1000, 2)

        total_ms = round((time.perf_counter() - start_pipeline) * 1000, 2)

        return {
            "transcript": stt_res.transcript,
            "intent_result": intent_res.model_dump(),
            "reply_text": parchi_data["card_text"],
            "reply_audio_bytes": tts_res.audio_bytes,
            "timings": {
                "stt_ms": stt_ms,
                "norm_ms": norm_ms,
                "parchi_ms": parchi_ms,
                "tts_ms": tts_ms,
                "total_ms": total_ms
            }
        }
