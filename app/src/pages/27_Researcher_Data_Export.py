import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Researcher Export")
st.write('Export collected researcher datasets for offline analysis or sharing.')

API_BASE = "http://web-api:4000"

# cache
@st.cache_data(ttl=300)
def fetch_all_data():
    response = requests.get(f"{API_BASE}/user_growing/", timeout=10)
    response.raise_for_status()
    return pd.DataFrame(response.json())

try:
    df_raw = fetch_all_data()
except Exception as e:
    st.error(f"Failed to load data from API: {e}")
    st.stop()

# normalise date columns so we can filter on them
for col in ("sown", "harvested", "created_at", "updated_at"):
    if col in df_raw.columns:
        df_raw[col] = pd.to_datetime(df_raw[col], errors="coerce")

# filters
st.subheader("Filter Data")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    # by season
    seasons = sorted(df_raw["season"].dropna().unique().tolist())
    selected_seasons = st.multiselect("Growing Season", seasons, placeholder="Select one or more seasons")

    # by crop type
    crops = sorted(df_raw["type_of_crop"].dropna().unique().tolist())
    selected_crops = st.multiselect("Crop Type", crops, placeholder="Select one or more crops")

with filter_col2:
    # by water source
    water_sources = sorted(df_raw["water_source"].dropna().unique().tolist())
    selected_water = st.multiselect("Water Source", water_sources, placeholder="Select water sources")

    # by farm_id
    farm_ids = sorted(df_raw["farm_id"].dropna().unique().tolist())
    selected_farms = st.multiselect("Farm ID", farm_ids, placeholder="Select one or more farm IDs")

with filter_col3:
    # columns to export
    all_columns = df_raw.columns.tolist()
    selected_columns = st.multiselect("Columns to Export", all_columns, default=all_columns)

# apply filters

df = df_raw.copy()

if selected_seasons:
    df = df[df["season"].isin(selected_seasons)]
if selected_crops:
    df = df[df["type_of_crop"].isin(selected_crops)]
if selected_water:
    df = df[df["water_source"].isin(selected_water)]
if selected_farms:
    df = df[df["farm_id"].isin(selected_farms)]

if selected_columns:
    df = df[[c for c in selected_columns if c in df.columns]]

st.divider()

# export
st.subheader(f"Preview  ·  {len(df):,} rows")
st.dataframe(df, use_container_width=True, height=300)

st.subheader("Export Options")
export_format = st.selectbox("Format", ["CSV", "JSON"])

if st.button("Prepare Export", type="primary"):
    if df.empty:
        st.warning("No data matches the current filters — nothing to export.")
    elif export_format == "CSV":
        st.download_button(
            "⬇ Download CSV",
            data=df.to_csv(index=False),
            file_name="growing_data_export.csv",
            mime="text/csv",
        )
    else:
        st.download_button(
            "⬇ Download JSON",
            data=df.to_json(orient="records", indent=2),
            file_name="growing_data_export.json",
            mime="application/json",
        )