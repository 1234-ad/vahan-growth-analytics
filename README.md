# VAHAN — Vehicle Registration Investor Dashboard (Backend Dev Assignment)

## Overview
This project produces an investor-friendly dashboard that visualizes vehicle registration trends and computes YoY (Year-over-Year) and QoQ (Quarter-over-Quarter) growth for vehicle categories (2W/3W/4W) and manufacturers (makers). The UI is built with Streamlit and the code is modular so it can be extended.

## Requirements
- Python 3.9+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Data Source
Primary reference: VAHAN public analytics dashboard (interactive) and public data mirrors. Example sources:
- VAHAN public dashboard (analytics.parivahan.gov.in) — interactive visualizations.
- India Data Portal / VAHAN datasets (maker-wise exports).

> **Important:** The VAHAN public dashboard often serves data via JavaScript and may present CAPTCHAs that block programmatic scraping. If you cannot programmatically fetch the data, download CSV exports from India Data Portal / data.gov.in or use a cleaned CSV export — place it at `data/vahan_data.csv`.

## CSV format expected
The app expects `data/vahan_data.csv` with at least the following columns:
- `date` — date in YYYY-MM-DD (if only year-month then use the first of the month)
- `vehicle_category` — e.g., `2W`, `3W`, `4W`
- `maker` — manufacturer name
- `count` — integer count of registrations for that row (periodic bucket)

## How to run (local)
1. Place `vahan_data.csv` under `data/`.
2. From project root:
   ```bash
   streamlit run src/app.py
   ```
3. Use sidebar controls to select date range, aggregation (monthly/quarterly/yearly), vehicle categories and makers.

## Notes about scraping & data collection
- The VAHAN interactive site uses JS and sometimes CAPTCHA; automated scraping can be blocked.
- Two recommended approaches:
  1. **Preferred (robust):** use public CSV exports / data mirrors (India Data Portal), which are easier to ingest.
  2. **Advanced (fragile):** automated scraping via Selenium (simulate a browser), solve/reuse CAPTCHA manually, or programmatic calls to discover internal JSON endpoints (only when permitted). If you plan to scrape, document the steps and respect terms-of-use.

## What I built
- Streamlit dashboard that computes and shows YoY & QoQ for categories and makers, allows filters and date range selection, and provides data downloads for filtered data and computed growth tables.

## Next steps / roadmap
- Add authentication + scheduling to auto-refresh dataset weekly.
- Add more investment KPIs (ARPU-style: revenue per registration if fee/revenue data is available).
- Add predictive short-term forecast (ARIMA/Prophet) for top manufacturers.
