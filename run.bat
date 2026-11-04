@echo off
if "%1"=="test" (
    python -m pytest -q -m "not live"
) else if "%1"=="test-live" (
    python -m pytest -q -m "live"
) else if "%1"=="cli" (
    python scripts/run_pipeline.py %2 %3 %4 %5
) else if "%1"=="" (
    python -m pytest -q -m "not live"
) else (
    python -m pytest -q -m "not live" %*
)
