import os
import time
import pandas as pd
from typing import List, Dict
from .psx_scraper import fetch_company
from .config import TARGET_PE_DEFAULT, SECTOR_PE_OVERRIDE


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def fair_value_pe(eps: float, sector: str | None) -> float:
    """Calculate fair value using EPS × P/E."""
    if eps is None or eps <= 0:
        return float("nan")

    pe = TARGET_PE_DEFAULT
    if sector:
        for key, val in SECTOR_PE_OVERRIDE.items():
            if key.lower() in sector.lower():
                pe = float(val)
                break
    return eps * pe


def run(symbols: List[str]) -> pd.DataFrame:
    """Fetch data for all symbols and return a DataFrame."""
    rows: List[Dict] = []

    for sym in symbols:
        try:
            d = fetch_company(sym)
        except Exception as e:
            d = {"symbol": sym, "error": str(e)}

        # Compute fair value
        fv = fair_value_pe(d.get("eps_latest"), d.get("sector_guess"))
        price = d.get("price")
        disc = None
        if price and fv and fv == fv and price > 0:
            disc = (fv - price) / price

        rows.append({
            "symbol": d.get("symbol", sym),
            "price": price,
            "eps_latest": d.get("eps_latest"),
            "fair_value_pe": fv,
            "discount_vs_fair": disc,
            "sector_guess": d.get("sector_guess"),
            "source_url": d.get("url"),
            "eps_series": "|".join(str(x) for x in (d.get("eps_series") or [])),
            "error": d.get("error")
        })

        time.sleep(0.7)  # Be polite to PSX servers

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["discount_vs_fair"], ascending=False)
    return df


def main():
    """Entry point: read tickers, fetch data, and save outputs."""
    symbols_file = os.path.join(DATA_DIR, "symbols.csv")

    if not os.path.exists(symbols_file):
        print("symbols.csv not found in data/. Please create one.")
        return

    with open(symbols_file, "r", encoding="utf-8") as f:
        symbols = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    df = run(symbols)

    # Save CSV
    out_csv = os.path.join(DATA_DIR, "stocks.csv")
    df.to_csv(out_csv, index=False)

    # Create simple HTML page
    html = df.to_html(index=False, justify="center")
    html_page = f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>PSX Fair-Value Screener</title>
<style>
body {{ font-family: system-ui, Arial, sans-serif; padding: 16px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }}
th {{ cursor: pointer; background: #f2f2f2; }}
</style>
</head>
<body>
<h2>PSX Fair-Value Screener (PE-based)</h2>
<p>Click headers to sort. <em>Educational use only.</em></p>
<div id="table">{html}</div>

<script>
// Simple table sorting
(function() {{
  const tbl = document.querySelector("table");
  const get = (r, c) => r.children[c].innerText || "";
  let asc = true;

  tbl.querySelectorAll("th").forEach((th, idx) => {{
    th.addEventListener("click", () => {{
      const rows = [...tbl.querySelectorAll("tbody tr")];
      rows.sort((a, b) => {{
        const A = get(a, idx).replace(/[^0-9.\-]/g, "");
        const B = get(b, idx).replace(/[^0-9.\-]/g, "");
        const aN = parseFloat(A), bN = parseFloat(B);
        const isNum = !isNaN(aN) && !isNaN(bN);
        if (isNum) return asc ? aN - bN : bN - aN;
        return asc ? get(a, idx).localeCompare(get(b, idx))
                   : get(b, idx).localeCompare(get(a, idx));
      }});
      rows.forEach(r => tbl.tBodies[0].appendChild(r));
      asc = !asc;
    }});
  }});
}})();
</script>

</body>
</html>"""

    out_html = os.path.join(DATA_DIR, "stocks.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_page)

    print(f"Wrote {out_csv} and {out_html}")


if __name__ == "__main__":
    main()
