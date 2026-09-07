import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_footprint_dataset

def render_lifestyle():
    st.header("Lifestyle Carbon Footprint Audit")
    st.caption(
        "Evaluate your estimated annual carbon footprint across household energy, diet, mobility, and consumption."
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Mobility & Travel")
        transport_mode = st.selectbox(
            "Primary Daily Transport",
            ["Public Transit (Bus/Train)", "Private Vehicle (Car/Motorcycle)", "Walk / Bicycle"],
            index=0
        )
        monthly_km = st.number_input("Estimated Monthly Travel (km)", min_value=0, max_value=10000, value=350, step=50)
        air_travel = st.selectbox(
            "Air Travel Frequency",
            ["Never", "Rarely (1-2 flights/year)", "Frequently (3-6 flights/year)", "Very Frequently (7+ flights/year)"],
            index=1
        )

        st.subheader("2. Diet & Food Habits")
        diet_type = st.selectbox("Dietary Pattern", ["Omnivore (Regular meat)", "Pescatarian", "Vegetarian", "Vegan"], index=0)
        grocery_bill = st.number_input("Monthly Grocery Spending ($ or equivalent)", min_value=20, max_value=2000, value=250, step=25)

    with col2:
        st.subheader("3. Home Energy & Utilities")
        heating_source = st.selectbox("Heating & Cooking Energy", ["Electricity", "Natural Gas", "LPG", "Wood / Coal"], index=0)
        energy_efficiency = st.selectbox("Use Energy-Efficient Appliances?", ["Yes", "Sometimes", "No"], index=1)
        daily_screen_hours = st.slider("Daily TV / PC Screen Time (Hours)", min_value=0, max_value=16, value=6)

        st.subheader("4. Waste & Consumption")
        waste_bags = st.slider("Waste Bags Disposed per Week", min_value=1, max_value=10, value=3)
        recycles = st.multiselect("Materials You Actively Recycle", ["Paper", "Plastic", "Glass", "Metal"], default=["Plastic", "Paper"])
        new_clothes = st.slider("New Clothing Items Purchased Monthly", min_value=0, max_value=20, value=2)

    # Calculation logic aligned with dataset emission factors
    # 1. Transport CO2 (kg/year)
    if "Private" in transport_mode:
        transport_annual = (monthly_km * 12) * 0.18
    elif "Public" in transport_mode:
        transport_annual = (monthly_km * 12) * 0.06
    else:
        transport_annual = (monthly_km * 12) * 0.01

    flight_factor = {"Never": 0, "Rarely (1-2 flights/year)": 450, "Frequently (3-6 flights/year)": 1400, "Very Frequently (7+ flights/year)": 3200}
    transport_annual += flight_factor.get(air_travel, 450)

    # 2. Diet CO2 (kg/year)
    diet_map = {"Omnivore (Regular meat)": 1850, "Pescatarian": 1250, "Vegetarian": 1050, "Vegan": 750}
    diet_annual = diet_map.get(diet_type, 1850) + (grocery_bill * 0.45)

    # 3. Energy CO2 (kg/year)
    heating_map = {"Electricity": 750, "Natural Gas": 950, "LPG": 850, "Wood / Coal": 1400}
    efficiency_multiplier = {"Yes": 0.8, "Sometimes": 1.0, "No": 1.25}
    energy_annual = (heating_map.get(heating_source, 800) + (daily_screen_hours * 35)) * efficiency_multiplier.get(energy_efficiency, 1.0)

    # 4. Waste & Consumption CO2 (kg/year)
    recycle_discount = max(0.65, 1.0 - (len(recycles) * 0.08))
    waste_annual = ((waste_bags * 52 * 4.5) + (new_clothes * 12 * 8.5)) * recycle_discount

    total_annual_kg = transport_annual + diet_annual + energy_annual + waste_annual
    total_annual_tonnes = total_annual_kg / 1000.0

    st.divider()
    st.subheader("Your Annual Footprint Summary")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Emissions", f"{total_annual_tonnes:.2f} t / year", help="Tonnes of CO2 equivalent per year")
    m2.metric("Transport Share", f"{(transport_annual / total_annual_kg * 100):.0f}%")
    m3.metric("Diet Share", f"{(diet_annual / total_annual_kg * 100):.0f}%")
    m4.metric("Home & Waste Share", f"{((energy_annual + waste_annual) / total_annual_kg * 100):.0f}%")

    # Category breakdown chart
    breakdown_df = pd.DataFrame([
        {"Category": "Mobility & Flights", "Emissions (kg CO2)": round(transport_annual, 1)},
        {"Category": "Diet & Food", "Emissions (kg CO2)": round(diet_annual, 1)},
        {"Category": "Home Energy", "Emissions (kg CO2)": round(energy_annual, 1)},
        {"Category": "Waste & Goods", "Emissions (kg CO2)": round(waste_annual, 1)}
    ])

    fig = px.bar(
        breakdown_df,
        x="Emissions (kg CO2)",
        y="Category",
        orientation="h",
        text="Emissions (kg CO2)",
        color="Category",
        color_discrete_sequence=["#2b5c8f", "#417d6b", "#c28236", "#8a5874"]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=260,
        xaxis_title="Annual Emissions (kg CO2 equivalent)",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

    # Benchmark vs Population Dataset
    st.write("**Benchmark vs Dataset Population**")
    median_kg = 2300.0
    diff_from_median = ((total_annual_kg - median_kg) / median_kg) * 100

    if diff_from_median > 20:
        st.warning(
            f"Your footprint ({total_annual_kg:.0f} kg/year) is **{abs(diff_from_median):.1f}% higher** than the baseline dataset average (2,300 kg/year)."
        )
    elif diff_from_median < -20:
        st.success(
            f"Your footprint ({total_annual_kg:.0f} kg/year) is **{abs(diff_from_median):.1f}% lower** than the baseline dataset average (2,300 kg/year)."
        )
    else:
        st.info(
            f"Your footprint ({total_annual_kg:.0f} kg/year) is roughly on par with the baseline dataset average (2,300 kg/year)."
        )

    # Tailored recommendations
    st.subheader("Key Improvement Opportunities")
    recs = []
    if transport_annual > 1200:
        recs.append("Opt for rail or bus on regional trips to reduce transportation emissions.")
    if diet_annual > 1400:
        recs.append("Introducing 1-2 plant-based days weekly can reduce annual dietary emissions by up to 20%.")
    if energy_annual > 1000:
        recs.append("Switch to LED lighting and turn off standby appliances to lower home energy draw.")
    if waste_annual > 400:
        recs.append("Expand composting and choose items with minimal single-use packaging.")

    if not recs:
        recs.append("Great job maintaining a well-balanced, low-carbon lifestyle!")

    for r in recs:
        st.markdown(f"- {r}")
