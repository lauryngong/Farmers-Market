import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Farmer: Crop Type Predictions")
st.write('Select available farming resources and environmental conditions.')

st.write('## Recommend crop to plant')

type_of_crop = st.selectbox('Crop Category', ['Root&tuber', 'bulbvegetables', 'cereals', 'colecrops', 'fibre crop', 'millets', 'oil seeds', 'pulses', 'sugar crops', 'vegetables'])
season = st.selectbox('Season', ['Zaid', 'kharif', 'rabi'])
water_source = st.selectbox('Water Source', ['irrigated', 'rainfed'])
sown = st.selectbox('Sowing Month', ['Apr', 'Dec', 'Jul', 'Jun', 'Mar', 'May', 'Nov', 'Oct'])
harvested = st.selectbox('Harvest Month', ['Apr', 'Jul', 'Jun', 'Mar', 'May', 'Oct', 'Sep'])
N = st.number_input('Soil Nitrogen (N)', min_value=0.0, value=50.0, step=1.0)
P = st.number_input('Soil Phosphorus (P)', min_value=0.0, value=50.0, step=1.0)
K = st.number_input('Soil Potassium (K)', min_value=0.0, value=50.0, step=1.0)
temperature = st.number_input('Average Temperature (°C)', value=25.0, step=0.5)
relative_humidity = st.number_input('Relative Humidity (%)', min_value=0.0, max_value=100.0, value=60.0, step=1.0)

if st.button('Predict'):
    logger.info(f'Prediction request- crop category: {type_of_crop}, season: {season}')
    try:
        response = requests.get(
            f'http://web-api:4000/crop/model3/prediction/{N}/{P}/{K}/{type_of_crop}/{temperature}/{season}/{sown}/{harvested}/{water_source}/{relative_humidity}'
        )
        response.raise_for_status()
        result = response.json()
        pred = result['prediction']

        st.success('Prediction complete!')
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label='Crop Category', value=type_of_crop)
        with m2:
            st.metric(label='Season', value=season)
        with m3:
            st.metric(label='Recommended Crop', value=pred)

    except Exception as e:
        logger.error(f'Prediction error: {e}')
        st.error(f'Could not retrieve prediction: {e}')