# PROJECT.md: GallaVaani (read after AGENTS.md and CONSTITUTION.md every session)

MISSION
Implement GallaVaani per .spec/ and ship a working, demo-able app for the Great Indian AI Internship Challenge 2026 (Gnani.ai).

FILL-INS (human, before Phase 0)
- Language(s): Spoken: Code-mixed Hinglish (`hi-IN` + `en-IN`, `format="codemix"`) + 1 regional Indian language (`gu-IN` / `mr-IN` / `kn-IN`). Code: Python 3.11+.
- Target user + core task (one sentence): Tier 2/3 Indian household shoppers and local kirana shopkeepers — converts noisy, code-mixed customer WhatsApp voice-note grocery orders into structured, price-estimated order slips (Parchis) that the shopkeeper can approve in 1 tap or override with a 5-second voice note without typing.
- Award category: Primary: "Real Deal" & "Mixed Vibes" | Secondary: "Noise Canceller", "Two-Person Army", "Small Town, Big Build".
- Stack per SDD: Python 3.11+, FastAPI, Pydantic v2, httpx, Redis + SQLite/PostgreSQL (cart state, `wamid` idempotency, 8s burst coalescer), ffmpeg (OGG/Opus audio slicing), pytest.
- Project test command (one command, e.g. `make test`): `pytest -q -m "not live"` (wrapped in `make test`; run `pytest -q -m live` manually at phase gates).
- Duo: A = core pipeline + evaluation; B = WhatsApp adapter + UI + docs. API key holder: Teammate A (holds `X-API-Key-ID` with 5,000 credits in `.env`; records real Gnani JSON/OGG responses into `tests/fixtures/` so Teammate B runs offline at zero credit cost).
- Build hours before freeze: ~32–36 hours per teammate across 4 days (Nov 4 to Nov 7 night = ~64–72 total person-hours).
- HARNESS CLI: ECC="node <path>/Antigravity-ECC/bin/ecc.js". Never run bare `npx antigravity-ecc`.

DEADLINES (today Nov 4, 2026)
Freeze Nov 7 night. Record and post Nov 8. Submit Nov 9. Hard deadline Nov 10, 11:59 PM IST, no extensions.

CHALLENGE RULES
- Use and name >=1 Gnani model/API. Each teammate is interviewed separately: both must be able to explain every module.
- Synthetic or consented data only. Never log phone numbers. Store no audio except test fixtures.
- 5,000 credits on one account: tests use recorded fixtures; live calls only at gates.
- Public post needs #GreatIndianAIInternshipChallenge and #GnaniAI. No bought engagement. State limitations honestly.

VERIFIED GNANI FACTS (docs/API_NOTES.md overrides this once it exists)
- STT REST: POST https://api.vachana.ai/stt/v3, multipart (audio_file, language_code e.g. hi-IN, format), header X-API-Key-ID. WAV/MP3/OGG/FLAC/AAC/M4A. Max 60 s (ideal <=30 s). 429 = rate limit.
- STT realtime: wss://api.vachana.ai/stt/v3/stream, raw PCM16 mono, 8/16 kHz.
- TTS: REST/SSE/WebSocket; can output OGG/Opus. Voice and model names differ across doc pages.
- Evon is open-weight, not on the API platform. Do not plan around it.
UNVERIFIED: language counts, Warp availability, any "Agent API", exact TTS path and voice list.

WHATSAPP FACTS (verify in Meta docs)
Voice notes must be OGG/Opus mono. Meta test number + temporary 24 h token. Webhook needs public HTTPS; free tunnel URLs change on restart.

SPRINT-MODE OVERRIDES TO THE 8-STAGE LOOP
- research: only Gnani + Meta docs -> docs/API_NOTES.md.
- plan: .spec/ IS the plan. Never run /spec or any command that writes into .spec/. `git diff --stat -- .spec` must be empty at every gate.
- test: tests first for logic and adapters, using recorded fixtures. Live tests tagged `live`, run by hand.
- implement: minimal code to green. No refactors outside the current module.
- review/verify: /review and `$ECC scan --strict` at phase gates; fix HIGH, log the rest in docs/KNOWN_ISSUES.md.
- remember: after each phase store 3-5 facts with `$ECC memory store` AND mirror them in docs/DECISIONS.md (memory.db is local; my teammate can't see it).
- improve: skipped until after submission (no instinct/dashboard).
- If a lifecycle hook blocks you, satisfy it (e.g. add the failing test); don't disable hooks.

TOOLBELT (Phase 0 fills in exact names from commands/ and docs/AGENT-CATALOG.md)
research: [/research | research-first]   tests: [/test | test-coverage-enforcer]   TDD: [/tdd | tdd-driver]   backend: [/python-fastapi | python-backend-engineer]   review: [/review | code-reviewer]   security: [$ECC scan --strict | security-auditor]

RULES
1. .gitignore (.env, .agents/, *.db, audio outputs) before the first commit. Never print or commit keys.
2. No silent redesign: propose in docs/DECISIONS.md and wait. Mark SDD ambiguity "# TODO(arch):".
3. docs/API_NOTES.md is ground truth for API behavior, not memory.
4. Non-Gnani services must be disclosed in DECISIONS.md and README.
5. End every phase with a completion report: done / gates passed / failed and why / next action / "what each human should be able to explain in an interview".
6. After 3 failures on one step, stop with diagnostics and options. If a phase overruns its time box by 50%, stop and propose a cut.
7. Small commits on branches a/... and b/...; don't touch the other person's module without asking.