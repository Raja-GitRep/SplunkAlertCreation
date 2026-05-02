import re
import requests

SCREENER_BASE_URL = "https://www.screener.in/company"
SCREENER_COMPANIES = [
    ("RELIANCE", "Reliance Industries"),
    ("TCS", "Tata Consultancy Services"),
    ("INFY", "Infosys"),
    ("HDFCBANK", "HDFC Bank"),
    ("ICICIBANK", "ICICI Bank"),
]


def clean_html_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_screener_metrics(html):
    metrics = {}
    for match in re.finditer(
        r'<li class="flex flex-space-between"[^>]*>.*?<span class="name">\s*(.*?)\s*</span>.*?<span class="nowrap value">(.*?)</span>',
        html,
        re.S,
    ):
        name = clean_html_text(match.group(1))
        value = clean_html_text(match.group(2))
        metrics[name] = value
    return metrics


def parse_number(value):
    cleaned = re.sub(r"[^0-9\.\-]", "", str(value))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def fetch_company_metrics(symbol):
    url = f"{SCREENER_BASE_URL}/{symbol}/"
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        timeout=20,
    )
    response.raise_for_status()
    metrics = parse_screener_metrics(response.text)
    return {
        "symbol": symbol,
        "market_cap": metrics.get("Market Cap", "N/A"),
        "stock_pe": metrics.get("Stock P/E", "N/A"),
        "roe": metrics.get("ROE", "N/A"),
        "eps": metrics.get("EPS", "N/A"),
        "pb": metrics.get("P/B", "N/A"),
        "dividend_yield": metrics.get("Dividend yield", "N/A"),
        "debt_equity": metrics.get("Debt / Equity", "N/A"),
    }


def fetch_live_screener_data():
    companies = []
    for symbol, name in SCREENER_COMPANIES:
        try:
            company = fetch_company_metrics(symbol)
            company["name"] = name
        except requests.RequestException as exc:
            company = {
                "symbol": symbol,
                "name": name,
                "market_cap": "Unable to load",
                "stock_pe": "Unable to load",
                "roe": "Unable to load",
                "eps": "Unable to load",
                "pb": "Unable to load",
                "dividend_yield": "Unable to load",
                "debt_equity": "Unable to load",
                "error": str(exc),
            }
        companies.append(company)
    return companies
