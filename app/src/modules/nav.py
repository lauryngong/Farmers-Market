# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About Our Project", icon="🧠")


# ---- Role: farmer ------------------------------------------------

def farmer_home():
    st.sidebar.page_link(
        "pages/01_Farmer_Home.py", label="Farmer Home", icon="👨‍🌾"
    )
    
def farmer_info():
    st.sidebar.page_link(
        "pages/02_Farm_Info.py", label="Your Farm Management", icon="🏡"
    )
    
def crop_prediction():
    st.sidebar.page_link(
        "pages/04_Crop_Predictions.py", label="Crop Type Suggestion", icon="🌾"
    )
    
def farmer_blog():
    st.sidebar.page_link(
        "pages/05_Farmer_Blog.py", label="Discussion Board", icon="💭"
    )

# ---- Role: policy-maker -----------------------------------------------------

def policy_home():
    st.sidebar.page_link(
        "pages/11_Policy_Home.py", label="Policy Maker Home", icon="🧑‍💼"
    )
    
def policy_map():
    st.sidebar.page_link(
        "pages/12_Policy_Map.py", label="Crop Price Map", icon="🗺️"
    )
    
def policy_compare():
    st.sidebar.page_link(
        "pages/13_Policy_Compare.py", label="Compare Farm Prices", icon="🚜"
    )
    
def policy_report():
    st.sidebar.page_link(
        "pages/14_Policy_Report.py", label="Report Maker", icon="📝"
    )
    
def policy_predictions():
    st.sidebar.page_link(
        "pages/15_Policy_Predictions.py", label="Crop Price Predictions", icon="🌾"
    )
    
def policy_blog():
    st.sidebar.page_link(
        "pages/17_Policy_Blog.py", label="Discussion Board", icon="💭"
    )

# ---- Role: researcher ----------------------------------------------------

def researcher_home():
    st.sidebar.page_link("pages/21_Researcher_Home.py", label="Home", icon="👨‍🔬")

def researcher_map():
    st.sidebar.page_link("pages/23_Researcher_Map.py", label="Map", icon="🗺️")

def researcher_conditions():
    st.sidebar.page_link("pages/24_Researcher_Conditions.py", label="Explore Crop Observations", icon="🌱")
    
def researcher_trends():
    st.sidebar.page_link("pages/25_Researcher_Trends.py", label="Explore Crop Trends", icon="📈")

def researcher_data_export():
    st.sidebar.page_link("pages/27_Researcher_Data_Export.py", label="Data Export", icon="🖥️")

def researcher_blog():
    st.sidebar.page_link("pages/28_Researcher_Blog.py", label="Discussion Board", icon="💭")

def researcher_compare():
    st.sidebar.page_link("pages/29_Researcher_Compare.py", label="Compare Crops", icon="⚖️")

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # App-wide button polish: rounded corners + subtle hover lift.
    # Purely cosmetic — injected here because SideBarLinks() runs on every page.
    st.markdown(
        """
        <style>
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.15s ease-in-out;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(46, 125, 50, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "farmer":
            farmer_home()
            farmer_info()
            crop_prediction()
            farmer_blog()

        if st.session_state["role"] == "policy_maker":
            policy_home()
            policy_map()
            policy_compare()
            policy_report()
            policy_predictions()
            policy_blog()

        if st.session_state["role"] == "researcher":
            researcher_home()
            researcher_map()
            researcher_conditions()
            researcher_trends()
            researcher_compare()
            researcher_data_export()
            researcher_blog()
    else:
        # Only show about for when not logged in
        about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
