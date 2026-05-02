# Project Usage Guide

This repository now contains two separate applications and a shared common package.

## Folder Structure

- `streamlit_app/` — Streamlit app for creating Splunk saved search alerts
- `fastapi_app/` — FastAPI app for stock market data and UI pages
- `common/` — Shared helper modules used by both applications

## Setup

1. Create and activate your Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Streamlit App

Launch the Streamlit app from the `streamlit_app` folder:

```bash
cd streamlit_app
streamlit run streamlit_splunk_alerts.py
```

Then open the URL shown by Streamlit in your browser.

### What it does

- Connects to a local Splunk Enterprise instance
- Creates a saved search alert with email action
- Updates the alert ACL to app-level sharing

## FastAPI App

Launch the FastAPI app from the `fastapi_app` folder:

```bash
cd fastapi_app
uvicorn fastapi_market:app --reload
```

Then open `http://127.0.0.1:8000` in your browser.

### What it does

- Serves a styled market overview homepage
- Provides a `/TodaysMarket` page with live Screener.in metrics
- Uses shared logic from `common/market_data.py`

## Shared Common Package

Both apps import reusable logic from `common/`:

- `common/splunk_alerts.py` — Splunk alert creation and ACL helpers
- `common/market_data.py` — Screener data fetching and parsing utilities

## Notes

- Keep the `common/` package sibling to both apps so imports work correctly.
- If you run inside a virtual environment, activate it before launching the apps.
