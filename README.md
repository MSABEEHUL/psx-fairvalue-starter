# PSX Fair‑Value Screener (free + simple)

This tiny project fetches **EPS** and **last price** for a list of PSX tickers from the public **PSX Data Portal** company pages,
then estimates a **fair value** using a *target P/E* you can tweak (default 10). It sorts by discount to fair value.

> **For learning only.** Always follow the PSX website Terms/Legal Notice. Do not redistribute or commercialize data.


## Quick start (local)
1) Install Python 3.10+  
2) `pip install -r requirements.txt`  
3) Put your tickers in `data/symbols.csv` (one symbol per line).  
4) Run: `python -m src.build_table`  
5) Open the output: `data/stocks.html` (a sortable table) or `streamlit run streamlit_app.py`

## What it does
- Grabs each company page like `https://dps.psx.com.pk/company/INIL`
- Parses **price** (e.g., `Rs.226.99`) and **EPS (Annual)** numbers shown on the *Financials* tab
- Uses the most recent **Annual EPS** as a rough EPS (TTM proxy)
- Computes **Fair Value = EPS × TARGET_PE** (defaults to 10, change per sector in `src/config.py`)
- Writes `data/stocks.csv` and `data/stocks.html`

## Deploy for free (optional)
- **Streamlit Community Cloud**: connect this repo and deploy `streamlit_app.py`
- **GitHub Actions** (included) runs daily to refresh data and commit results back to the repo

## Notes & limits
- HTML on PSX pages can change. Update the parser rules in `src/psx_scraper.py` if needed.
- Prices and EPS shown on company pages are provided via PSX/Capital Stake. Treat numbers as **approximate**.
- Personal/educational use only — respect the **PSX Data Portal Legal Notice**.


