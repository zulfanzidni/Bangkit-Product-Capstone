import sys
import streamlit as st
from pathlib import Path

# Ensure sys.path contains root and streamlit_app directory
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
for p in [str(APP_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Set basic page configuration
st.set_page_config(
    page_title="EcoMeter - Carbon & Climate Tracker",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import sub-modules
from calculator import render_calculator
from lifestyle import render_lifestyle
from catalog import render_catalog
from global_trends import render_global_trends
from utils import MODEL_MOBILE_PATH, MODEL_ML_PATH

def render_overview():
    st.header("About EcoMeter")
    st.write(
        """
        **EcoMeter** is an urban carbon footprint tracking and climate resilience application, originally developed as a **Bangkit Academy Capstone Project**.
        
        The platform combines machine learning models and environmental datasets to help individuals measure, understand, and reduce their daily resource consumption and emissions.
        """
    )

    st.subheader("Project Structure & Data Sources")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("**Machine Learning**")
        st.caption("TensorFlow Lite regression models trained on vehicle fuel consumption and emissions datasets.")
        m_status = "Available" if (MODEL_MOBILE_PATH.exists() or MODEL_ML_PATH.exists()) else "Missing"
        st.write(f"- Model Status: `{m_status}`")
        st.write("- Architecture: Dense Regression Network")
        st.write("- Target: CO2 Emissions (g/km)")

    with c2:
        st.write("**Datasets**")
        st.caption("Empirical vehicle and global climate indicators.")
        st.write("- Canada Vehicle Emissions (7,385 records)")
        st.write("- Individual Carbon Footprints (10,000 records)")
        st.write("- Global Sustainable Energy (2000–2020)")

    with c3:
        st.write("**Original Architecture**")
        st.caption("Multi-tier cloud and mobile deployment.")
        st.write("- Mobile App: Android (Kotlin, TFLite runtime)")
        st.write("- Cloud Backend: Node.js Hapi + Firestore")
        st.write("- Analytics: Streamlit Python Web Platform")

    st.divider()
    st.subheader("Actionable Recommendations")
    st.write(
        """
        Adapted from the EcoMeter lifestyle recommendations database:
        1. **Sustainable Mobility**: Shift short urban trips (<3 km) to walking or cycling. Use rapid transit for longer daily commutes.
        2. **Household Energy**: Turn off idle devices and optimize cooling/heating setpoints.
        3. **Conscious Consumption**: Reduce single-use items, practice regular sorting for recyclable paper and plastics, and curb food waste.
        4. **Community Engagement**: Support local tree planting and climate resilience initiatives.
        """
    )


def main():
    # Sidebar navigation
    st.sidebar.title("EcoMeter")
    st.sidebar.caption("Tracking Urban Footprints for Climate Resilience")

    nav_choice = st.sidebar.radio(
        "Navigation",
        [
            "Trip Calculator",
            "Lifestyle Footprint",
            "Vehicle Catalog",
            "Global Climate Trends",
            "Project Overview"
        ],
        index=0
    )

    st.sidebar.divider()
    st.sidebar.caption("Bangkit Capstone Product Suite")

    # Render selected view
    if nav_choice == "Trip Calculator":
        render_calculator()
    elif nav_choice == "Lifestyle Footprint":
        render_lifestyle()
    elif nav_choice == "Vehicle Catalog":
        render_catalog()
    elif nav_choice == "Global Climate Trends":
        render_global_trends()
    elif nav_choice == "Project Overview":
        render_overview()


if __name__ == "__main__":
    main()
