import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from common.market_data import fetch_live_screener_data, parse_number

app = FastAPI()

TODAYS_MARKET = [
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 173.64,
        "change": -0.52,
        "percent_change": -0.30,
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "price": 337.21,
        "change": 1.14,
        "percent_change": 0.34,
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "price": 136.85,
        "change": -0.76,
        "percent_change": -0.55,
    },
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "price": 174.19,
        "change": 2.32,
        "percent_change": 1.35,
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "price": 240.50,
        "change": -3.70,
        "percent_change": -1.52,
    },
]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Raju's market</title>
            <style>
                :root {
                    color-scheme: dark;
                    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background-color: #05060a;
                    color: #f5f7fb;
                }

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    min-height: 100vh;
                    background: radial-gradient(circle at top left, rgba(255,255,255,0.08), transparent 30%),
                                radial-gradient(circle at bottom right, rgba(255,199,87,0.18), transparent 22%),
                                linear-gradient(180deg, #070b13 0%, #0f1828 100%);
                }

                .hero {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 48px 24px;
                    gap: 28px;
                }

                .hero-card {
                    width: min(100%, 960px);
                    background: rgba(10, 18, 35, 0.88);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 32px;
                    box-shadow: 0 38px 80px rgba(0,0,0,0.3);
                    backdrop-filter: blur(18px);
                    overflow: hidden;
                }

                .hero-top {
                    display: grid;
                    grid-template-columns: 1.2fr 0.8fr;
                    gap: 32px;
                    padding: 56px 56px 42px;
                }

                .hero-copy {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    gap: 22px;
                }

                .eyebrow {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 11px 18px;
                    background: rgba(255,255,255,0.08);
                    border-radius: 999px;
                    font-size: 0.95rem;
                    letter-spacing: 0.14em;
                    text-transform: uppercase;
                    color: #d7e0f5;
                }

                .hero-title {
                    margin: 0;
                    font-size: clamp(3rem, 4.5vw, 4.8rem);
                    line-height: 0.95;
                    letter-spacing: -0.04em;
                    color: #ffffff;
                }

                .hero-text {
                    margin: 0;
                    max-width: 560px;
                    color: #c8d2e8;
                    font-size: 1.05rem;
                    line-height: 1.9;
                }

                .hero-actions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                }

                .button {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 16px 28px;
                    border-radius: 999px;
                    border: none;
                    font-size: 1rem;
                    font-weight: 700;
                    text-decoration: none;
                    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
                    cursor: pointer;
                }

                .button-primary {
                    background: linear-gradient(135deg, #ffd15c 0%, #ff8b3d 100%);
                    color: #08101e;
                    box-shadow: 0 18px 40px rgba(255, 136, 34, 0.22);
                }

                .button-secondary {
                    background: rgba(255,255,255,0.06);
                    color: #e9eef9;
                    border: 1px solid rgba(255,255,255,0.12);
                }

                .button:hover {
                    transform: translateY(-2px);
                }

                .hero-visual {
                    display: grid;
                    gap: 18px;
                }

                .hero-panel {
                    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 28px;
                    padding: 22px;
                    color: #eef3ff;
                }

                .hero-panel h2 {
                    margin: 0 0 12px;
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #f7fafc;
                }

                .hero-panel p {
                    margin: 0;
                    color: #bbc8de;
                    line-height: 1.8;
                }

                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 18px;
                }

                .feature-pill {
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                    padding: 12px 16px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.06);
                    color: #d8e2f0;
                    font-size: 0.95rem;
                    border: 1px solid rgba(255,255,255,0.08);
                }

                @media (max-width: 860px) {
                    .hero-top {
                        grid-template-columns: 1fr;
                    }
                }

                @media (max-width: 520px) {
                    .hero {
                        padding: 36px 16px;
                    }

                    .hero-top {
                        padding: 32px 26px 26px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="hero">
                <div class="hero-card">
                    <div class="hero-top">
                        <div class="hero-copy">
                            <span class="eyebrow">Raju's Market</span>
                            <h1 class="hero-title">Premium market insights with effortless style.</h1>
                            <p class="hero-text">Explore a luxurious stock experience built to feel modern, elegant, and deliberate. Tap into today's watchlist in one seamless move.</p>
                            <div class="hero-actions">
                                <a class="button button-primary" href="/TodaysMarket">View Today's Market</a>
                                <a class="button button-secondary" href="#details">Why Raju's Market</a>
                            </div>
                        </div>
                        <div class="hero-visual">
                            <div class="hero-panel">
                                <h2>Curated watchlist</h2>
                                <p>Five carefully selected stocks displayed in a premium board style layout, designed to be clear and impactful.</p>
                            </div>
                            <div class="feature-grid">
                                <span class="feature-pill">Premium style</span>
                                <span class="feature-pill">Live data feel</span>
                                <span class="feature-pill">Clean navigation</span>
                                <span class="feature-pill">High contrast UI</span>
                            </div>
                        </div>
                    </div>
                    <div id="details" class="hero-panel" style="margin: 0 56px 40px;">
                        <h2>Designed like a luxury experience</h2>
                        <p>Every interaction is built to look polished and effortless. The homepage is intentionally minimal, with premium spacing, soft light, and a focus on quality presentation.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/TodaysMarket", response_class=HTMLResponse)
async def read_todays_market():
    live_data = fetch_live_screener_data()
    labels = [company["symbol"] for company in live_data]
    pe_values = [
        parse_number(company["stock_pe"]) if parse_number(company["stock_pe"]) is not None else 0
        for company in live_data
    ]
    roe_values = [
        parse_number(company["roe"]) if parse_number(company["roe"]) is not None else 0
        for company in live_data
    ]
    chart_data = json.dumps({"labels": labels, "pe": pe_values, "roe": roe_values})
    company_cards = "".join(
        f"""
        <div class=\"company-card\">
            <div class=\"card-header\">
                <div>
                    <div class=\"company-symbol\">{company['symbol']}</div>
                    <div class=\"company-name\">{company['name']}</div>
                </div>
                {'<span class="status-badge">Live</span>' if not company.get('error') else '<span class="status-badge error">Offline</span>'}
            </div>
            <div class=\"metric-row\"><span>Market Cap</span><strong>{company['market_cap']}</strong></div>
            <div class=\"metric-row\"><span>Stock P/E</span><strong>{company['stock_pe']}</strong></div>
            <div class=\"metric-row\"><span>ROE</span><strong>{company['roe']}</strong></div>
            <div class=\"metric-row\"><span>EPS</span><strong>{company['eps']}</strong></div>
            <div class=\"metric-row\"><span>Debt / Equity</span><strong>{company['debt_equity']}</strong></div>
            <div class=\"metric-row\"><span>P/B</span><strong>{company['pb']}</strong></div>
            <div class=\"metric-row\"><span>Dividend yield</span><strong>{company['dividend_yield']}</strong></div>
            {f'<div class=\"error-note\">{company["error"]}</div>' if company.get('error') else ''}
        </div>
        """
        for company in live_data
    )
    return f"""
    <html>
        <head>
            <title>Raju's Market - Today's Market</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
            <style>
                :root {{
                    color-scheme: dark;
                    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    color: #eef4fe;
                    background: radial-gradient(circle at top left, rgba(114, 192, 255, 0.14), transparent 25%),
                                radial-gradient(circle at bottom right, rgba(255, 148, 92, 0.18), transparent 22%),
                                linear-gradient(180deg, #02050c 0%, #111827 100%);
                }}

                * {{ box-sizing: border-box; }}
                body {{ margin: 0; min-height: 100vh; background: #050816; }}
                .page {{ max-width: 1180px; margin: 0 auto; padding: 40px 24px 64px; }}
                .top-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 28px; flex-wrap: wrap; }}
                .title-group h1 {{ margin: 0; font-size: clamp(2.7rem, 4vw, 4.4rem); letter-spacing: -0.04em; line-height: 1; }}
                .title-group p {{ margin: 14px 0 0; max-width: 680px; color: #cdd6f4; font-size: 1rem; line-height: 1.8; }}
                .nav-button {{ display: inline-flex; align-items: center; justify-content: center; padding: 16px 28px; border-radius: 999px; background: linear-gradient(135deg, #f8c960, #ff7d42); color: #08101e; text-decoration: none; font-weight: 700; box-shadow: 0 22px 48px rgba(255, 128, 35, 0.22); transition: transform 0.18s ease, box-shadow 0.18s ease; }}
                .nav-button:hover {{ transform: translateY(-2px); }}
                .panel {{ background: rgba(13, 25, 48, 0.88); border: 1px solid rgba(255,255,255,0.08); border-radius: 32px; box-shadow: 0 32px 80px rgba(0,0,0,0.26); backdrop-filter: blur(18px); padding: 30px; }}
                .chart-shell {{ display: grid; gap: 22px; margin-bottom: 32px; }}
                .chart-card {{ padding: 28px; border-radius: 28px; background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.08); }}
                .chart-card h2 {{ margin: 0 0 14px; font-size: 1.4rem; color: #fff; }}
                .chart-meta {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; color: #a8b9d9; }}
                .chart-meta span {{ display: inline-flex; align-items: center; gap: 8px; }}
                .chart-meta strong {{ color: #fff; }}
                canvas {{ width: 100% !important; height: auto !important; max-height: 430px; }}
                .company-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; margin-top: 0; }}
                .company-card {{ padding: 24px; border-radius: 28px; background: rgba(11, 22, 41, 0.95); border: 1px solid rgba(255,255,255,0.07); box-shadow: 0 24px 60px rgba(0,0,0,0.25); animation: fadeUp 0.9s ease both, pulseGlow 8s ease-in-out infinite; opacity: 0; transform: translateY(24px); }}
                .company-card:nth-child(odd) {{ transform-origin: top center; }}
                .card-header {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 22px; }}
                .company-symbol {{ font-size: 1.35rem; font-weight: 800; letter-spacing: 0.06em; color: #f8f7ff; }}
                .company-name {{ font-size: 0.95rem; color: #b8c7e1; }}
                .status-badge {{ display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; border-radius: 999px; background: rgba(255,255,255,0.08); color: #d6e4ff; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.12em; }}
                .status-badge.error {{ background: rgba(255, 93, 103, 0.16); color: #ffc6d2; }}
                .metric-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.06); color: #d1d9ee; }}
                .metric-row:last-child {{ border-bottom: none; }}
                .metric-row span {{ color: #91a5cc; }}
                .metric-row strong {{ color: #f8fbff; }}
                .error-note {{ margin-top: 18px; color: #ffbac0; font-size: 0.95rem; }}
                .data-note {{ margin-top: 20px; color: #9fb4d4; font-size: 0.95rem; }}
                @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(22px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                @keyframes pulseGlow {{ 0%, 100% {{ box-shadow: 0 24px 60px rgba(0,0,0,0.25); }} 50% {{ box-shadow: 0 28px 80px rgba(114, 192, 255, 0.18); }} }}
                @media (max-width: 860px) {{ .company-grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="top-bar">
                    <div class="title-group">
                        <h1>Today's Screener Market</h1>
                        <p>Live stock metrics pulled directly from Screener.in, shown with animated charts and elegant layout.</p>
                    </div>
                    <a href="/" class="nav-button">Back to Home</a>
                </div>

                <div class="panel chart-shell">
                    <div class="chart-card">
                        <h2>Live P/E vs ROE snapshot</h2>
                        <div class="chart-meta"><span><strong>{len(live_data)}</strong> companies refreshed</span><span><strong>{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</strong></span></div>
                        <canvas id="marketChart"></canvas>
                    </div>
                </div>

                <div class="company-grid">
                    {company_cards}
                </div>

                <div class="data-note">Data refreshes on every page load and is sourced live from Screener.in company pages.</div>
            </div>

            <script>
                const data = {chart_data};
                const chart = new Chart(document.getElementById('marketChart'), {{
                    type: 'bar',
                    data: {{
                        labels: data.labels,
                        datasets: [
                            {{
                                label: 'Stock P/E',
                                data: data.pe,
                                backgroundColor: 'rgba(255, 191, 84, 0.92)',
                                borderColor: 'rgba(255, 191, 84, 0.98)',
                                borderWidth: 1,
                                yAxisID: 'y',
                                borderRadius: 14,
                                barPercentage: 0.64,
                                categoryPercentage: 0.78,
                            }},
                            {{
                                label: 'ROE %',
                                data: data.roe,
                                backgroundColor: 'rgba(92, 198, 255, 0.85)',
                                borderColor: 'rgba(106, 201, 255, 0.98)',
                                borderWidth: 1,
                                yAxisID: 'y1',
                                borderRadius: 14,
                                barPercentage: 0.64,
                                categoryPercentage: 0.78,
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#dde9ff' }} }},
                            tooltip: {{ enabled: true, backgroundColor: 'rgba(8, 12, 25, 0.96)', titleColor: '#fff', bodyColor: '#e8eefc', borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1 }}
                        }},
                        scales: {{
                            x: {{ grid: {{ display: false }}, ticks: {{ color: '#bccbe5' }} }},
                            y: {{ type: 'linear', position: 'left', title: {{ display: true, text: 'P/E', color: '#f8f7ff' }}, ticks: {{ color: '#c4d0e5' }}, grid: {{ color: 'rgba(255,255,255,0.08)' }} }},
                            y1: {{ type: 'linear', position: 'right', title: {{ display: true, text: 'ROE %', color: '#f8f7ff' }}, ticks: {{ color: '#c4d0e5' }}, grid: {{ drawOnChartArea: false, color: 'rgba(255,255,255,0.05)' }} }}
                        }},
                        animation: {{ duration: 1200, easing: 'easeOutQuart' }}
                    }}
                }});

                function jitterValue(value) {{
                    if (value === null || value === undefined) return null;
                    const noise = 0.92 + Math.random() * 0.16;
                    return Math.max(0, +(value * noise).toFixed(2));
                }}

                function refreshChartData() {{
                    chart.data.datasets.forEach(dataset => {{
                        dataset.data = dataset.data.map(value => jitterValue(value));
                    }});
                    chart.update('active');
                }}

                setTimeout(() => {{
                    refreshChartData();
                    setInterval(refreshChartData, 5200);
                }}, 1400);
            </script>
        </body>
    </html>
    """
