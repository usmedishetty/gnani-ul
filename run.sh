#!/usr/bin/env bash
TASK="${1:-test}"

case "$TASK" in
    "test")
        python3 -m pytest -q -m "not live"
        ;;
    "test-live")
        python3 -m pytest -q -m "live"
        ;;
    *)
        python3 -m pytest -q -m "not live"
        ;;
esac

