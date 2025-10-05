import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="PSX Fair‑Value Screener", layout="wide")
st.title("PSX Fair‑Value Screener (PE‑based)")

data_path = Path("data/stocks.csv")
if not data_path.exists():
    st.warning("Run `python -m src.build_table` once to create data/stocks.csv")
else:
    df = pd.read_csv(data_path)
    st.caption("Educational use only. Numbers are approximate/paraphrased from PSX company pages.")
    col1, col2 = st.columns(2)
    with col1:
        sector = st.text_input("Filter by sector text", "")
    with col2:
        min_disc = st.slider("Min discount vs fair (%)", -100, 100, 0, 1)
    if sector:
        df = df[df["sector_guess"].fillna("").str.contains(sector, case=False, na=False)]
    if "discount_vs_fair" in df.columns:
        df["discount_%"] = (df["discount_vs_fair"] * 100).round(2)
        df = df.drop(columns=["discount_vs_fair"])
        df = df.sort_values(by="discount_%", ascending=False)
        df = df[df["discount_%"] >= min_disc]
    st.dataframe(df, use_container_width=True)
