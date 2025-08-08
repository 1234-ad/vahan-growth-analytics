# src/app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from src.data_fetch import read_local_csv
from src.data_processing import prepare_timeseries, compute_growth
import plotly.express as px

st.set_page_config(layout="wide", page_title="VAHAN — Investor Dashboard")

st.title("VAHAN — Vehicle Registration Dashboard (Investor view)")
st.markdown("Interactive dashboard showing QoQ & YoY growth for vehicle categories and makers. Use the controls on the left to filter data.")

@st.cache_data
def load_data(path=None):
    df = read_local_csv(path)
    return df

df = load_data()

# Sidebar controls
st.sidebar.header("Controls")
min_date = df['date'].min()
max_date = df['date'].max()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
agg_choice = st.sidebar.selectbox("Aggregation", options=["Monthly", "Quarterly", "Yearly"], index=0)
vehicle_categories = st.sidebar.multiselect("Vehicle categories", options=sorted(df['vehicle_category'].unique()), default=sorted(df['vehicle_category'].unique()))
makers = st.sidebar.multiselect("Makers (manufacturers)", options=sorted(df['maker'].unique()), default=sorted(df['maker'].unique())[:10])

# filter dataframe
start, end = date_range
mask = (df['date'] >= pd.to_datetime(start)) & (df['date'] <= pd.to_datetime(end)) & (df['vehicle_category'].isin(vehicle_categories)) & (df['maker'].isin(makers))
filtered = df.loc[mask].copy()

# aggregate
freq_map = {"Monthly":"M","Quarterly":"Q","Yearly":"Y"}
freq = freq_map[agg_choice]
agg = prepare_timeseries(filtered, freq=freq)

# compute growth
growth = compute_growth(agg, group_by='vehicle_category', freq=freq)

# Show top KPIs
st.subheader("Key metrics")
total_current = filtered['count'].sum()
latest_period = agg['period'].max() if not agg.empty else None
kpi_cols = st.columns(4)
kpi_cols[0].metric("Total registrations (selected)", f"{int(total_current):,}")
kpi_cols[1].metric("Selected periods", f"{agg['period'].nunique() if not agg.empty else 0}")

cat_last = growth[growth['period'] == latest_period].groupby('vehicle_category').agg({'count':'sum','yoy_pct':'mean','qoq_pct':'mean'}).reset_index() if latest_period is not None else pd.DataFrame()

for i, cat in enumerate(vehicle_categories[:3]):
    if cat_last.empty or cat not in cat_last['vehicle_category'].values:
        kpi_cols[min(3,i+1)].metric(f"{cat}", "0", delta="--")
    else:
        row = cat_last[cat_last['vehicle_category']==cat].iloc[0]
        kpi_cols[min(3,i+1)].metric(f"{cat}", f"{int(row['count']):,}", delta=f"YoY: {row['yoy_pct']}% / QoQ: {row['qoq_pct']}%")

st.markdown("---")

# Trends plot
st.subheader("Trend by vehicle category")
fig = px.line(agg.groupby(['period','vehicle_category'], as_index=False)['count'].sum(), x='period', y='count', color='vehicle_category', markers=True)
fig.update_layout(xaxis_title="Period", yaxis_title="Registered vehicles")
st.plotly_chart(fig, use_container_width=True)

# Maker trend (top selected makers)
st.subheader("Trend by Maker (manufacturer)")
maker_agg = agg.groupby(['period','maker'], as_index=False)['count'].sum()
maker_totals = maker_agg.groupby('maker')['count'].sum().sort_values(ascending=False).head(8).index.tolist()
display_makers = [m for m in makers if m in maker_totals] or list(maker_totals)
fig2 = px.line(maker_agg[maker_agg['maker'].isin(display_makers)], x='period', y='count', color='maker', markers=True)
fig2.update_layout(xaxis_title="Period", yaxis_title="Registered vehicles")
st.plotly_chart(fig2, use_container_width=True)

# Percent-change table
st.subheader("YoY & QoQ growth (table)")
growth_table = compute_growth(agg, group_by='maker', freq=freq)
last_n = st.sidebar.slider("Show last N periods", min_value=1, max_value=24, value=6)
periods = sorted(growth_table['period'].unique())[-last_n:]
gt = growth_table[growth_table['period'].isin(periods) & growth_table['maker'].isin(makers)]
st.dataframe(gt.sort_values(['period','count'], ascending=[False,False]).reset_index(drop=True))

# Download buttons
@st.cache_data
def to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download filtered raw data (CSV)", to_csv_bytes(filtered), file_name="vahan_filtered.csv", mime="text/csv")
st.download_button("Download growth table (CSV)", to_csv_bytes(growth_table), file_name="vahan_growth.csv", mime="text/csv")

st.markdown("---")
st.info("Data source: VAHAN public dashboard / mirrors. If you don't have a local CSV, download maker-wise or category-wise CSV from India Data Portal / analytics.parivahan.gov.in (see README).")
