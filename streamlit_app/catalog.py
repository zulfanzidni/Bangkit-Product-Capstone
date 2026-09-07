import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_vehicle_catalog

def render_catalog():
    st.header("Vehicle Emissions Catalog")
    st.caption("Search, filter, and compare factory emissions across real-world vehicles.")

    df = load_vehicle_catalog()
    if df.empty:
        st.warning("Vehicle emissions dataset not found.")
        return

    # Filters
    c1, c2, c3 = st.columns(3)
    with c1:
        makes = ["All Makes"] + sorted(df["Make"].dropna().unique().tolist())
        selected_make = st.selectbox("Make", makes)
    with c2:
        classes = ["All Classes"] + sorted(df["Vehicle Class"].dropna().unique().tolist())
        selected_class = st.selectbox("Vehicle Class", classes)
    with c3:
        min_eng = float(df["Engine Size(L)"].min())
        max_eng = float(df["Engine Size(L)"].max())
        engine_range = st.slider("Engine Size (L)", min_eng, max_eng, (min_eng, max_eng), step=0.1)

    filtered_df = df.copy()
    if selected_make != "All Makes":
        filtered_df = filtered_df[filtered_df["Make"] == selected_make]
    if selected_class != "All Classes":
        filtered_df = filtered_df[filtered_df["Vehicle Class"] == selected_class]

    filtered_df = filtered_df[
        (filtered_df["Engine Size(L)"] >= engine_range[0]) &
        (filtered_df["Engine Size(L)"] <= engine_range[1])
    ]

    st.write(f"Showing **{len(filtered_df):,}** matching vehicles")

    display_cols = [
        "Make", "Model", "Vehicle Class", "Engine Size(L)", "Cylinders",
        "Fuel Consumption Comb (L/100 km)", "CO2 Emissions(g/km)"
    ]
    st.dataframe(
        filtered_df[display_cols].sort_values(by="CO2 Emissions(g/km)"),
        use_container_width=True,
        hide_index=True
    )

    # Side-by-Side Comparator
    st.divider()
    st.subheader("Side-by-Side Model Comparison")
    st.caption("Select two vehicles from the dataset to compare fuel economy and emissions.")

    col_v1, col_v2 = st.columns(2)
    # Create unique label for selection
    df["Vehicle_Label"] = df["Make"] + " " + df["Model"] + " (" + df["Engine Size(L)"].astype(str) + "L, " + df["Cylinders"].astype(str) + " cyl)"
    unique_labels = sorted(df["Vehicle_Label"].unique().tolist())

    with col_v1:
        v1_label = st.selectbox("Vehicle A", unique_labels, index=0)
        v1_data = df[df["Vehicle_Label"] == v1_label].iloc[0]
    with col_v2:
        # Pick a different index for default B
        v2_idx = min(10, len(unique_labels) - 1)
        v2_label = st.selectbox("Vehicle B", unique_labels, index=v2_idx)
        v2_data = df[df["Vehicle_Label"] == v2_label].iloc[0]

    annual_km = st.number_input("Comparison Annual Mileage (km)", min_value=1000, max_value=100000, value=15000, step=1000)

    # Comparison metrics table
    v1_co2_rate = float(v1_data["CO2 Emissions(g/km)"])
    v2_co2_rate = float(v2_data["CO2 Emissions(g/km)"])

    v1_annual_kg = (v1_co2_rate * annual_km) / 1000.0
    v2_annual_kg = (v2_co2_rate * annual_km) / 1000.0

    v1_fuel_rate = float(v1_data["Fuel Consumption Comb (L/100 km)"])
    v2_fuel_rate = float(v2_data["Fuel Consumption Comb (L/100 km)"])

    v1_annual_fuel = (v1_fuel_rate / 100.0) * annual_km
    v2_annual_fuel = (v2_fuel_rate / 100.0) * annual_km

    diff_co2 = v2_annual_kg - v1_annual_kg
    diff_fuel = v2_annual_fuel - v1_annual_fuel

    comp_summary = pd.DataFrame({
        "Metric": [
            "Engine Size",
            "Cylinders",
            "Combined Fuel Consumption",
            "CO2 Emission Rate",
            f"Annual CO2 ({annual_km:,} km)",
            f"Annual Fuel ({annual_km:,} km)"
        ],
        "Vehicle A": [
            f"{v1_data['Engine Size(L)']} L",
            f"{v1_data['Cylinders']}",
            f"{v1_fuel_rate:.1f} L/100 km",
            f"{v1_co2_rate:.0f} g/km",
            f"{v1_annual_kg:.1f} kg",
            f"{v1_annual_fuel:.1f} L"
        ],
        "Vehicle B": [
            f"{v2_data['Engine Size(L)']} L",
            f"{v2_data['Cylinders']}",
            f"{v2_fuel_rate:.1f} L/100 km",
            f"{v2_co2_rate:.0f} g/km",
            f"{v2_annual_kg:.1f} kg",
            f"{v2_annual_fuel:.1f} L"
        ]
    })
    st.dataframe(comp_summary, use_container_width=True, hide_index=True)

    if diff_co2 > 0:
        st.info(f"Vehicle A emits **{abs(diff_co2):.1f} kg less CO2** and saves **{abs(diff_fuel):.1f} L of fuel** annually compared to Vehicle B.")
    elif diff_co2 < 0:
        st.info(f"Vehicle B emits **{abs(diff_co2):.1f} kg less CO2** and saves **{abs(diff_fuel):.1f} L of fuel** annually compared to Vehicle A.")
    else:
        st.info("Both vehicles share identical annual emissions and fuel consumption.")
