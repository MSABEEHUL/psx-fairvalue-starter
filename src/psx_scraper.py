import re, time, math
from typing import Dict, Optional, List, Tuple
import requests
from bs4 import BeautifulSoup

BASE = "https://dps.psx.com.pk/company/{symbol}"

num_re = re.compile(r"[-+]?\(?\d[\d,]*\.?\d*\)?")

def _to_float(txt: str) -> Optional[float]:
    if not txt: 
        return None
    t = txt.strip().replace(",", "")
    # Handle "(0.50)" negative style
    if t.startswith("(") and t.endswith(")"):
        t = "-" + t[1:-1]
    try:
        return float(t)
    except:
        return None

def extract_numbers_after(label: str, text: str, limit: int = 8) -> List[float]:
    """Find `label` in text, then collect up to `limit` numeric tokens following it."""
    i = text.find(label)
    if i == -1:
        return []
    tail = text[i + len(label): i + len(label) + 2000]  # small window
    found = num_re.findall(tail)
    vals = []
    for tok in found[:limit]:
        vals.append(_to_float(tok))
    return [v for v in vals if v is not None]

def fetch_company(symbol: str, timeout: int = 25) -> Dict:
    url = BASE.format(symbol=symbol.strip().upper())
    r = requests.get(url, timeout=timeout, headers={
        "User-Agent": "Mozilla/5.0 (Educational Bot)"
    })
    r.raise_for_status()
    html = r.text
    soup = BeautifulSoup(html, "lxml")

    # 1) Try to get a clean text blob (more robust across templates)
    text = soup.get_text(separator=" ", strip=True)

    # 2) Price: look for "Rs." pattern
    price = None
    m = re.search(r"Rs\.\s*([0-9,]+\.\d+|[0-9,]+)", text)
    if m:
        price = _to_float(m.group(1))

    # 3) Sector (nice to have; can refine fair value per sector)
    sector = None
    # Try to find sector label near top ("ENGINEERING", "CEMENT", etc.).
    # We'll grab the first ALL‑CAPS word that matches a common sector pattern window.
    m2 = re.search(r"\b(BANKS|CEMENT|ENGINEERING|FERTILIZER|OIL & GAS|TEXTILE|TECHNOLOGY.+?|PHARMA|AUTOMOBILE.+?)\b", text)
    if m2:
        sector = m2.group(0)

    # 4) EPS (Annual): find the first "Financials" -> "Annual" -> "EPS" block
    # Strategy: after the word "Financials" and "Annual", find "EPS" and read the numbers after it.
    # Fallback: just search the first "EPS" in the page and take up to 6 numbers.
    eps_vals = []
    fin_idx = text.find("Financials")
    if fin_idx != -1:
        sub = text[fin_idx: fin_idx + 8000]
        # prefer Annual block if we can spot it
        ann_idx = sub.find("Annual")
        if ann_idx != -1:
            sub2 = sub[ann_idx: ann_idx + 4000]
            eps_vals = extract_numbers_after("EPS", sub2, limit=8)
    if not eps_vals:
        eps_vals = extract_numbers_after("EPS", text, limit=8)

    # Most recent EPS is usually the first number after "EPS"
    latest_eps = eps_vals[0] if eps_vals else None

    return {
        "symbol": symbol.upper(),
        "url": url,
        "price": price,
        "sector_guess": sector,
        "eps_latest": latest_eps,
        "eps_series": eps_vals,
    }
