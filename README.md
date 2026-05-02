# Splunk Alert Creator with Streamlit

A simple project with two separate applications and a shared helper package.

## Project layout

- `streamlit_app/` — Streamlit app for Splunk alert creation
- `fastapi_app/` — FastAPI app with market dashboard pages
- `common/` — Shared utilities imported by both apps

## Requirements

- Splunk Enterprise installed and running locally (for the Streamlit app)
- Splunk management port reachable (default: `8089`)
- Python 3.8+ with dependencies installed

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. See the app-specific launch instructions in `docs/USAGE.md`.

## Notes

- The root `README.md` now points to `docs/USAGE.md` for usage details and commands.
- The Streamlit app and the FastAPI app are intentionally separated into their own folders.
- Shared logic is kept in `common/` so both apps stay modular and easy to maintain.
