import logging
logger = logging.getLogger(__name__)

import glob
import os

import requests
import streamlit as st
from modules.nav import SideBarLinks

# crop images live in app/src/assets/crops/ with mixed extensions (.jpeg/.jpg/.webp)
CROP_IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "crops")


def crop_image_path(crop: str) -> str | None:
    """Return the on-disk path of a crop's image regardless of extension, or None."""
    matches = glob.glob(os.path.join(CROP_IMG_DIR, f"{crop}_img.*"))
    return matches[0] if matches else None

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Farmer: Crop Type Predictions")

tab1, tab2 = st.tabs(["Predict", "Saved Predictions"])


# ─────────────────────────────────────────────
# TAB 1 — set a prediction
# ─────────────────────────────────────────────
with tab1:
    st.subheader("Recommend crop to plant")
    st.write("Select available farming resources and environmental conditions.")
    st.caption("Note on N, P, K for soil: If a fertilizer bag says 10-15-10, it means it contains 10% Nitrogen, 15% Phosphorus, and 10% Potassium. " \
    "Plants need different ratios depending on what they do.")

    user_id = st.session_state.get('user_id')
    type_of_crop = st.selectbox(
        'Crop Category',
        ['Root&tuber', 'bulbvegetables', 'cereals', 'colecrops', 'fibre crop', 'millets', 'oil seeds', 'pulses', 'sugar crops', 'vegetables'],
        help='The broad category of crop you intend to grow. The model uses this to narrow recommendations to crops within the chosen group.'
    )
    season_labels = {'Zaid': 'Summer (Zaid)', 'kharif': 'Monsoon (Kharif)', 'rabi': 'Winter (Rabi)'}
    season = st.selectbox(
        'Season', ['Zaid', 'kharif', 'rabi'], format_func=lambda s: season_labels[s],
        help='The growing season: Zaid (summer), Kharif (monsoon/rainy), or Rabi (winter). Different crops thrive in different seasons.'
    )
    water_source = st.selectbox(
        'Water Source', ['irrigated', 'rainfed'],
        help='How the field gets its water: "irrigated" (supplied via canals/wells/pumps) or "rainfed" (relies on natural rainfall).'
    )
    sown = st.date_input(
        'Sowing Date',
        help='The date you plan to plant the seeds. Only the month is sent to the model.'
    )
    harvested = st.date_input(
        'Harvest Date',
        help='The date you expect to harvest the crop. Only the month is sent to the model.'
    )
    crop_duration = st.slider(
        'Crop Duration (days)', min_value=0, max_value=150, value=100, step=1,
        help='Number of days from sowing to harvest. Helps match crops with a similar growing cycle.'
    )
    temperature = st.slider(
        'Average Temperature (°C)', min_value=0.0, max_value=40.0, value=25.0, step=0.5,
        help='The average air temperature expected during the growing period, in degrees Celsius.'
    )
    water_required = st.slider(
        'Water Required (mm)', min_value=0, max_value=2500, value=800, step=10,
        help='Total water the crop needs over its full growth cycle, measured in millimetres.'
    )
    relative_humidity = st.slider(
        'Relative Humidity (%)', min_value=0.0, max_value=80.0, value=60.0, step=1.0,
        help='Average air moisture during the growing period, as a percentage. Higher values mean more humid conditions.'
    )
    N = st.slider(
        'Soil Nitrogen (N)', min_value=0.0, max_value=100.0, value=50.0, step=1.0,
        help='Nitrogen content of the soil. Nitrogen drives leaf and stem growth.'
    )
    P = st.slider(
        'Soil Phosphorus (P)', min_value=0.0, max_value=60.0, value=30.0, step=1.0,
        help='Phosphorus content of the soil. Phosphorus supports root development and flowering.'
    )
    K = st.slider(
        'Soil Potassium (K)', min_value=0.0, max_value=60.0, value=30.0, step=1.0,
        help='Potassium content of the soil. Potassium supports overall plant health and disease resistance.'
    )

    if st.button('Predict'):
        logger.info(f'Prediction request- crop category: {type_of_crop}, season: {season}')
        # model only wants the month abbrev (e.g. 'Jun'); we keep the full dates for saving
        sown_month = sown.strftime('%B')[:3]
        harvested_month = harvested.strftime('%B')[:3]
        try:
            response = requests.get(
                f'http://web-api:4000/crop/model3/prediction/{N}/{P}/{K}/{type_of_crop}/{temperature}/{season_labels[season]}/{sown_month}/{harvested_month}/{water_source}/{relative_humidity}/{crop_duration}/{water_required}'
            )
            response.raise_for_status()
            result = response.json()
            preds = result['predictions']

            st.session_state['last_pred']={
                "farmer_id": user_id,
                "type_of_crop": type_of_crop,
                "sown": sown.isoformat(),
                "harvested": harvested.isoformat(),
                "water_source": water_source,
                "predicted_crops": preds, 
            } #save pred

            st.success('Prediction complete!')
            m1, m2 = st.columns(2)
            with m1:
                st.metric(label='Crop Category', value=type_of_crop)
            with m2:
                lbl=season
                if lbl =='Kharif': 
                    lbl= 'Monsoon (Kharif)'
                elif lbl =='Zaid': 
                    lbl= 'Summer (Zaid)'
                else:
                    lbl= 'Winter (Rabi)'

                st.metric(label='Season', value=lbl)

            st.write('### Recommended crops (most likely first)')
            for rank, crop in enumerate(preds, start=1):
                st.write(f'{rank}. {crop}')
                img_path = crop_image_path(crop)
                if img_path:
                    st.image(img_path, caption=f'image of {crop}', width=200)
                else:
                    st.caption(f'(no image available for {crop})')


        except Exception as e:
            logger.error(f'Prediction error: {e}')
            st.error(f'Could not retrieve prediction: {e}')

    if 'last_pred' in st.session_state:
        if st.button("Save Prediction"):
            r=requests.post('http://web-api:4000/pred/pred',json=st.session_state['last_pred'])
            if r.status_code==201:
                saved = r.json().get("saved", 1)
                st.success(f"Saved {saved} prediction record(s)!")
            else:
                st.error(f"Save failed: {r.text}")


# ─────────────────────────────────────────────
# TAB 2 — view past predictions
# ─────────────────────────────────────────────
with tab2:
    st.subheader("View saved predictions")

    user_id = st.session_state.get('user_id')
    try:
        r = requests.get('http://web-api:4000/pred/pastpreds')
        r.raise_for_status()
        rows = r.json()

        # keep only the logged-in farmer's saved predictions
        if user_id is not None:
            rows = [row for row in rows if row.get('farmer_id') == user_id]

        if not rows:
            st.info("No saved predictions yet. Make a prediction in the first tab and click Save.")
        else:
            # filter controls (built from this farmer's saved rows; empty = show all)
            def sorted_unique(field):
                return sorted({row[field] for row in rows if row.get(field) is not None})

            f1, f2, f3 = st.columns(3)
            with f1:
                crop_filter = st.multiselect("Predicted crop", sorted_unique("predicted_crop"))
            with f2:
                type_filter = st.multiselect("Crop category", sorted_unique("type_of_crop"))
            with f3:
                water_filter = st.multiselect("Water source", sorted_unique("water_source"))

            filtered = [
                row for row in rows
                if (not crop_filter or row.get("predicted_crop") in crop_filter)
                and (not type_filter or row.get("type_of_crop") in type_filter)
                and (not water_filter or row.get("water_source") in water_filter)
            ]

            # farmer_id is only used for filtering above; pred_id is internal too.
            # don't show either in the table
            for row in filtered:
                row.pop('farmer_id', None)
                row.pop('pred_id', None)

            if filtered:
                st.dataframe(filtered, use_container_width=True)
            else:
                st.info("No saved predictions match the selected filters.")
    except Exception as e:
        st.error(f"Could not load saved predictions: {e}")