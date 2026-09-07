import streamlit as st
import pandas as pd
from datetime import date
from utils import (
    predict_emissions_tflite,
    get_emission_equivalents,
    get_travel_mode_comparison,
)

def render_calculator():
    st.header("Vehicle Trip Carbon Calculator")
    st.caption("Estimate carbon emissions based on vehicle specifications and trip distance.")

    # Initialize trip log in session state if not present
    if "trip_log" not in st.session_state:
        st.session_state.trip_log = []

    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("Vehicle & Trip Details")
        trip_date = st.date_input("Date", value=date.today())
        vehicle_type = st.selectbox("Vehicle Type", ["Car", "Motorcycle"])

        if vehicle_type == "Car":
            engine_capacity = st.number_input(
                "Engine Capacity (CC)", min_value=600, max_value=6500, value=1500, step=100
            )
            cylinder_count = st.selectbox("Cylinders", [3, 4, 6, 8, 10, 12], index=1)
            fuel_class = st.selectbox(
                "Fuel Consumption Category",
                ["Small (Up to 1500 cc)", "Medium (Up to 3000 cc)", "Large (Over 3000 cc)"]
            )
        else:
            engine_capacity = st.number_input(
                "Engine Capacity (CC)", min_value=50, max_value=1800, value=150, step=25
            )
            cylinder_count = st.selectbox("Cylinders", [1, 2, 4], index=0)
            fuel_class = st.selectbox(
                "Engine Category",
                ["125 cc or less", "250 cc", "500 cc or more"]
            )

        distance_km = st.number_input(
            "Trip Distance (km)", min_value=0.5, max_value=2000.0, value=15.0, step=1.0
        )

        log_trip_btn = st.button("Calculate & Add to Trip Log", type="primary")

    # Run Prediction
    rate_g_per_km, total_g = predict_emissions_tflite(
        vehicle_type=vehicle_type,
        engine_capacity_cc=float(engine_capacity),
        cylinder_count=int(cylinder_count),
        fuel_class=fuel_class,
        distance_km=float(distance_km)
    )

    equivalents = get_emission_equivalents(total_g)

    if log_trip_btn:
        st.session_state.trip_log.append({
            "Date": str(trip_date),
            "Vehicle": vehicle_type,
            "Engine (CC)": int(engine_capacity),
            "Distance (km)": float(distance_km),
            "Rate (g/km)": rate_g_per_km,
            "Total CO2 (kg)": equivalents["kg_co2"]
        })
        st.success("Trip added to log below.")

    with col_result:
        st.subheader("Calculation Result")

        m1, m2 = st.columns(2)
        m1.metric(label="Total Emissions", value=f"{equivalents['kg_co2']:.2f} kg", help="Total CO2 produced for this trip")
        m2.metric(label="Emission Rate", value=f"{rate_g_per_km:.1f} g/km", help="CO2 emitted per kilometer")

        st.divider()
        st.write("**Environmental Equivalencies**")
        e1, e2, e3 = st.columns(3)
        e1.metric(label="Gasoline Burned", value=f"{equivalents['liters_gasoline']:.2f} L")
        e2.metric(label="Annual Tree Offset", value=f"{equivalents['trees_yearly']:.2f} trees")
        e3.metric(label="Phone Charges", value=f"{equivalents['smartphone_charges']:,}")

        st.divider()
        st.write("**Comparison with Alternative Modes**")
        comp_data = get_travel_mode_comparison(float(distance_km), total_g)
        comp_df = pd.DataFrame(comp_data)
        st.dataframe(
            comp_df[["Mode", "Trip CO2 (kg)", "Difference vs Current (g)"]],
            hide_index=True,
            use_container_width=True
        )

    # Trip Log & Summary Section
    st.divider()
    st.subheader("Your Logged Trips")
    if st.session_state.trip_log:
        log_df = pd.DataFrame(st.session_state.trip_log)
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        total_distance = log_df["Distance (km)"].sum()
        total_co2_kg = log_df["Total CO2 (kg)"].sum()

        s1, s2, s3 = st.columns(3)
        s1.metric("Total Trips", f"{len(log_df)}")
        s2.metric("Cumulative Distance", f"{total_distance:.1f} km")
        s3.metric("Cumulative CO2", f"{total_co2_kg:.2f} kg")

        if st.button("Clear Trip Log"):
            st.session_state.trip_log = []
            st.rerun()
    else:
        st.info("No trips logged yet in this session. Calculate and click 'Add to Trip Log' above to track your usage.")
