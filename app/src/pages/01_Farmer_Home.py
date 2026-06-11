import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Farmer, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('View Your Farm Management',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/02_Farm_Info.py')

if st.button('View Crop Type Suggestions',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/04_Crop_Predictions.py')

if st.button('View Discussion Board',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/05_Farmer_Blog.py')
