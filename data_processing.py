# src/data_processing.py
import pandas as pd
from typing import Tuple

def prepare_timeseries(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """
    freq: 'M' monthly, 'Q' quarterly, 'Y' yearly
    Expects df with columns: date (datetime), vehicle_category, maker, count
    Returns aggregated DataFrame with columns ['period','vehicle_category','maker','count'].
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    if freq == 'M':
        df['period'] = df['date'].dt.to_period('M').dt.to_timestamp()
    elif freq == 'Q':
        df['period'] = df['date'].dt.to_period('Q').dt.start_time
    elif freq in ('Y','A'):
        df['period'] = df['date'].dt.to_period('Y').dt.start_time
    else:
        raise ValueError("freq must be 'M','Q', or 'Y'")

    agg = df.groupby(['period','vehicle_category','maker'], as_index=False)['count'].sum()
    return agg

def compute_growth(agg: pd.DataFrame, group_by: str='vehicle_category', freq='M') -> pd.DataFrame:
    """
    Compute YoY and QoQ growth for each group_by dimension.
    agg: aggregated rows with columns: ['period','vehicle_category','maker','count']
    group_by: 'vehicle_category' or 'maker'
    freq: 'M' monthly, 'Q' quarterly, 'Y' yearly - controls shift distances
    Returns DataFrame with period, group_by, count, yoy_pct, qoq_pct
    """
    df = agg.groupby(['period', group_by], as_index=False)['count'].sum()
    df = df.sort_values(['period', group_by])
    # pivot to wide
    df_wide = df.set_index(['period', group_by]).unstack(fill_value=0)
    if isinstance(df_wide.columns, pd.MultiIndex):
        df_wide = df_wide['count']
    df_wide = df_wide.sort_index()

    if freq == 'M':
        yoy = df_wide.pct_change(periods=12) * 100
        qoq = df_wide.pct_change(periods=3) * 100
    elif freq == 'Q':
        yoy = df_wide.pct_change(periods=4) * 100
        qoq = df_wide.pct_change(periods=1) * 100
    elif freq in ('Y','A'):
        yoy = df_wide.pct_change(periods=1) * 100
        qoq = pd.DataFrame(0, index=df_wide.index, columns=df_wide.columns)
    else:
        yoy = df_wide.pct_change(periods=12) * 100
        qoq = df_wide.pct_change(periods=3) * 100

    df_long = df_wide.reset_index().melt(id_vars='period', var_name=group_by, value_name='count')
    yoy_long = yoy.reset_index().melt(id_vars='period', var_name=group_by, value_name='yoy_pct')
    qoq_long = qoq.reset_index().melt(id_vars='period', var_name=group_by, value_name='qoq_pct')

    merged = df_long.merge(yoy_long, on=['period', group_by], how='left').merge(qoq_long, on=['period', group_by], how='left')
    merged['yoy_pct'] = merged['yoy_pct'].round(2)
    merged['qoq_pct'] = merged['qoq_pct'].round(2)
    return merged

def top_makers_in_period(agg: pd.DataFrame, period, top_n:int=10):
    df = agg[agg['period'] == period]
    res = df.groupby('maker')['count'].sum().sort_values(ascending=False).head(top_n).reset_index()
    return res
