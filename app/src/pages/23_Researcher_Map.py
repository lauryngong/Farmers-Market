import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"


# ── Data fetching via REST API ───────────────────────────────────
@st.cache_data(ttl=300)
def load_map_data(season: str) -> pd.DataFrame:
    params = {}
    if season != "All":
        params["season"] = season
    r = requests.get(f"{API_BASE}/user_growing/map-data", params=params)
    r.raise_for_status()
    return pd.DataFrame(r.json())


@st.cache_data(ttl=300)
def load_farm_history(farm_id: int) -> pd.DataFrame:
    r = requests.get(f"{API_BASE}/user_growing/farm/{farm_id}")
    r.raise_for_status()
    return pd.DataFrame(r.json())


# ── Color mapping ────────────────────────────────────────────────
CROP_COLORS = {
    "vegetables":      [29,  158, 117],
    "sugar crops":     [127, 119, 221], 
    "Root&tuber":      [216,  90,  48],   
    "pulses":          [186, 117,  23], 
    "oil seeds":       [55,  138, 221],
    "millets":         [48,  131, 104], 
    "fibre crop":      [212,  83, 126], 
    "colecrops":       [230, 190,  50], 
    "cereals":         [200,  80,  80],   
    "bulbvegetables":  [100, 180, 100],   
}
WATER_COLORS = {
    "Irrigated": [29, 158, 117],
    "Rainfed":   [216, 90,  48],
}

def assign_color(df: pd.DataFrame, color_by: str) -> pd.DataFrame:
    df = df.copy()
    
    if color_by == "Crop type":
        def get_crop_color(row):
            # Only mark as no data if dominant_crop is actually missing
            if pd.isna(row['dominant_crop']) or row['dominant_crop'] == '':
                return [128, 128, 128]
            return CROP_COLORS.get(row['dominant_crop'], [136, 135, 128])
        
        df["color"] = df.apply(get_crop_color, axis=1)
        
    elif color_by == "Water source":
        def get_water_color(row):
            # Check if we have valid data for water source
            if row['record_count'] == 0 or pd.isna(row['has_irrigated']):
                return [128, 128, 128]
            return WATER_COLORS["Irrigated"] if row['has_irrigated'] else WATER_COLORS["Rainfed"]
        
        df["color"] = df.apply(get_water_color, axis=1)
        
    else:  # Temperature
        t_min, t_max = df["avg_temp"].min(), df["avg_temp"].max()
        def temp_to_color(row):
            # Check if we have valid temperature data
            if pd.isna(row['avg_temp']) or row['record_count'] == 0:
                return [128, 128, 128]
            norm = (row['avg_temp'] - t_min) / max(t_max - t_min, 1)
            return [
                int(133 + (216 - 133) * norm),
                int(183 - (183 - 90)  * norm),
                int(235 - (235 - 48)  * norm),
            ]
        df["color"] = df.apply(temp_to_color, axis=1)
    
    return df


# ── Legend helpers ───────────────────────────────────────────────
def rgb_to_hex(rgb: list) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb[:3])

def render_legend_swatch(label: str, color: list):
    hex_color = rgb_to_hex(color)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
        f'<div style="width:13px;height:13px;border-radius:50%;background:{hex_color};flex-shrink:0;"></div>'
        f'<span style="font-size:13px;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Page ─────────────────────────────────────────────────────────
st.title("Farm map")
st.write("View all farms and their overall respective crops on the map")
st.caption("Each dot is one farm, and the color represents the selected filter.")

col1, col2 = st.columns([2, 1])
with col1:
    color_by = st.segmented_control(
        "Color by",
        ["Crop type", "Water source", "Temperature"],
        default="Crop type",
    )
with col2:
    season = st.pills(
            "Season",
            ["All", "Monsoon (Kharif)", "Winter (Rabi)", "Summer (Zaid)"],
            default="All",
        )

# Load data — handle empty result gracefully
try:
    df = load_map_data(season)
except requests.HTTPError as e:
    st.error(f"Could not load map data: {e}")
    st.stop()

if df.empty:
    st.info("No farm data found for the selected filters.")
    st.stop()

df = assign_color(df, color_by)

# Stats bar
c1, c2, c3, c4 = st.columns(4)
c1.metric("Farms shown",  len(df))
c2.metric("Countries",    df["country"].nunique())
c3.metric("Crop types",   df["dominant_crop"].nunique())
c4.metric("Avg temp",     f"{df['avg_temp'].mean():.1f}°C")

# Map
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["longitude", "latitude"],  # match column names from API
    get_fill_color="color",
    get_radius=15000,
    pickable=True,
    auto_highlight=True,
    highlight_color=[255, 255, 255, 80],
)

view = pdk.ViewState(
    latitude=df["latitude"].mean(),
    longitude=df["longitude"].mean(),
    zoom=3,
    pitch=0,
)

tooltip = {
    "html": (
        "<b>Farm #{farm_id} — {farm_name}</b><br/>"
        "{country}<br/>"
        "Dominant crop: {dominant_crop}<br/>"
        "Avg temp: {avg_temp}°C · Humidity: {avg_humidity}%<br/>"
        "Records: {record_count}"
    ),
    "style": {
        "backgroundColor": "white",
        "color": "#333",
        "fontSize": "12px",
        "padding": "8px",
    }
}

st.pydeck_chart(
    pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip),
    use_container_width=True,
    height=420,
)

# ── Legend ───────────────────────────────────────────────────────
st.markdown("**Legend**")

if color_by == "Crop type":
    # Only show crop types actually present in the current data
    present_crops = set(df["dominant_crop"].dropna().unique())
    entries = [
        (crop, color)
        for crop, color in CROP_COLORS.items()
        if crop in present_crops
    ] + [("No data", [128, 128, 128])]
    legend_cols = st.columns(4)
    for i, (label, color) in enumerate(entries):
        with legend_cols[i % 4]:
            render_legend_swatch(label, color)

elif color_by == "Water source":
    legend_cols = st.columns(4)
    for i, (label, color) in enumerate([
        ("Irrigated", WATER_COLORS["Irrigated"]),
        ("Rainfed",   WATER_COLORS["Rainfed"]),
        ("No data",   [128, 128, 128]),
    ]):
        with legend_cols[i]:
            render_legend_swatch(label, color)

else:  # Temperature gradient
    t_min = df["avg_temp"].min()
    t_max = df["avg_temp"].max()
    cool_hex = rgb_to_hex([133, 183, 235])
    warm_hex = rgb_to_hex([216,  90,  48])
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
        f'  <span style="font-size:13px;">{t_min:.1f}°C</span>'
        f'  <div style="flex:1;min-width:120px;max-width:240px;height:13px;border-radius:7px;'
        f'       background:linear-gradient(to right,{cool_hex},{warm_hex});"></div>'
        f'  <span style="font-size:13px;">{t_max:.1f}°C</span>'
        f'  <div style="display:flex;align-items:center;gap:6px;margin-left:12px;">'
        f'    <div style="width:13px;height:13px;border-radius:50%;background:#808080;flex-shrink:0;"></div>'
        f'    <span style="font-size:13px;">No data</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )