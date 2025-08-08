# src/data_fetch.py
import pandas as pd
from pathlib import Path
import requests
from typing import Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "vahan_data.csv"

def read_local_csv(path: Optional[str] = None) -> pd.DataFrame:
    p = Path(path) if path else DATA_PATH
    df = pd.read_csv(p, parse_dates=['date'], dayfirst=False)
    # Basic normalization
    df.rename(columns=lambda c: c.strip().lower(), inplace=True)
    # ensure expected columns exist
    expected = {'date','vehicle_category','maker','count'}
    if not expected.issubset(set(df.columns)):
        raise ValueError(f"CSV missing columns. Found: {df.columns.tolist()} Expected at least: {expected}")
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

def attempt_api_example():
    """
    PLACEHOLDER: try to query analytics.parivahan.gov.in or other endpoints.
    Many pages load data via JS; if an endpoint is accessible you can use requests.
    Example pseudocode below — replace with working endpoints if available.
    """
    url = "https://analytics.parivahan.gov.in/analytics/rest/api/1.0/some-endpoint"
    headers = {"Accept": "application/json"}
    params = {"from": "2019-01-01", "to": "2025-07-31", "groupBy": "maker,vehicle_category"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code == 200:
        return pd.json_normalize(r.json()['data'])
    else:
        raise ConnectionError(f"API request failed {r.status_code}: {r.text[:200]}")

if __name__ == "__main__":
    # quick test
    df = read_local_csv()
    print("Loaded rows:", len(df))
