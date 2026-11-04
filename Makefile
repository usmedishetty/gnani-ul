.PHONY: test test-live clean

test:
	pytest -q -m "not live"

test-live:
	pytest -q -m "live"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

