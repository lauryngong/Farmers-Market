import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title="About Farmers Market")
SideBarLinks(show_home=True)

st.title("About Farmers Market")
st.divider()

# What is FarmCast
st.markdown("## What is Farmers Market?")
st.write("""
Farmers Market is a data-driven platform that helps farmers, researchers, and policymakers make smarter agricultural decisions. By combining environmental, agricultural, and economic data into a single application, Farmers Market allows users to analyze farming conditions, predict future outcomes, monitor environmental risks, and support sustainable land-use planning.

The platform combines machine learning models, interactive visualizations, community discussion tools, and reporting features to transform complex agricultural data into actionable insights.
""")

st.divider()

# Team
st.markdown("## Meet the Team")

r1, r2= st.columns(2)

with r1:
    st.image("assets/headshots/headshot.jpg", width=300)
    st.markdown("**NICOLE STEKOL**")
    st.write("Short bio or description here.")

with r2:
    st.image("assets/headshots/IMG_2392.JPG", width=200)
    st.markdown("**LAURYN GONG**")
    st.write("Hi, I’m Lauryn Gong! I’m a rising second year student at Northeastern studying computer science and business!")


r3, r4= st.columns(2)

with r3:
   # st.image("assets/team3.png", width=150)
    st.markdown("**ELISE WIZEMANN**")
    st.write("Short bio or description here.")

with r4:
    st.image("assets/headshots/minjuPhoto.jpg", width=250)
    st.markdown("**MINJU SUNG**")
    st.write("Hello, I'm a 3rd year Computer Science student with minor in Mathematics at Northeastern University. " \
    "When I'm not working on technical projects or exploring new data models, I enjoy hiking, reading, or competing as a member of Northeastern's Debate Society.")

st.divider()

# Data sources
st.markdown("## Data Sources")

ds1, ds2, ds3 = st.columns(3)

with ds1:
    st.markdown("#### 📊 Eurostat")
    st.write("YOUR EUROSTAT DESCRIPTION HERE")
    st.markdown("[eurostat.ec.europa.eu](https://ec.europa.eu/eurostat)")

with ds2:
    st.markdown("#### 🌤 Open-Meteo")
    st.write("YOUR OPEN-METEO DESCRIPTION HERE")
    st.markdown("[open-meteo.com](https://open-meteo.com)")

with ds3:
    st.markdown("#### 🔬 Mendeley Data")
    st.write("The raw dataset is collected by integrating multiple data " \
    "sources such as soil properties, climate factors, nutrient levels, " \
    "crop characteristics, and agricultural factors. The environemental features are then used to predict the best crop type for the input values.")
    st.markdown("[mendeley.com](https://data.mendeley.com/datasets/vynxnppr7j/1)")
    
st.divider()
st.caption("Farmers Market — Built as part of a data systems course.")

