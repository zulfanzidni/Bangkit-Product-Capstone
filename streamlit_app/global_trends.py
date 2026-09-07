import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_global_energy_dataset

def render_global_trends():
    st.header("Global Energy & Climate Insights")
    st.caption("Explore historical trajectories (2000–2020) for renewable adoption, electricity access, and emissions.")

    df = load_global_energy_dataset()
    if df.empty:
        st.warning("Global sustainable energy dataset not found.")
        return

    countries = sorted(df["Entity"].dropna().unique().tolist())
    default_idx = countries.index("Indonesia") if "Indonesia" in countries else 0

    col_select, col_empty = st.columns([1, 1])
    with col_select:
        selected_country = st.selectbox("Select Country", countries, index=default_idx)

    country_df = df[df["Entity"] == selected_country].sort_values(by="Year")

    if country_df.empty:
        st.info("No data available for the selected country.")
        return

    # Recent metrics
    latest_row = country_df.dropna(subset=["Year"]).iloc[-1]
    latest_year = int(latest_row["Year"])

    st.subheader(f"Snapshot: {selected_country} ({latest_year})")
    m1, m2, m3 = st.columns(3)

    elec_acc = latest_row.get("Access to electricity (% of population)", None)
    m1.metric(
        "Electricity Access",
        f"{elec_acc:.1f}%" if pd.notnull(elec_acc) else "N/A"
    )

    ren_share = latest_row.get("Renewable energy share in the total final energy consumption (%)", None)
    m2.metric(
        "Renewable Share",
        f"{ren_share:.1f}%" if pd.notnull(ren_share) else "N/A"
    )

    co2_val = latest_row.get("Value_co2_emissions_kt_by_country", None)
    m3.metric(
        "Annual CO2 Emissions",
        f"{co2_val:,.0f} kt" if pd.notnull(co2_val) else "N/A"
    )

    st.divider()

    # Chart 1: Renewable Share over time
    st.write("**1. Renewable Energy Share in Final Consumption (%)**")
    ren_data = country_df[["Year", "Renewable energy share in the total final energy consumption (%)"]].dropna()
    if not ren_data.empty:
        fig_ren = px.line(
            ren_data,
            x="Year",
            y="Renewable energy share in the total final energy consumption (%)",
            markers=True,
            line_shape="linear"
        )
        fig_ren.update_traces(line_color="#2b6b55")
        fig_ren.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="% Share")
        st.plotly_chart(fig_ren, use_container_width=True)
    else:
        st.info("No time-series data available for renewable share.")

    # Chart 2: Electricity Generation by Source (TWh)
    st.write("**2. Electricity Generation by Source (TWh)**")
    gen_cols = ["Electricity from fossil fuels (TWh)", "Electricity from renewables (TWh)", "Electricity from nuclear (TWh)"]
    valid_cols = [c for c in gen_cols if c in country_df.columns]

    if valid_cols:
        gen_df = country_df[["Year"] + valid_cols].dropna(how="all", subset=valid_cols)
        gen_melted = gen_df.melt(id_vars=["Year"], value_vars=valid_cols, var_name="Source", value_name="TWh")
        gen_melted["Source"] = gen_melted["Source"].str.replace("Electricity from ", "").str.replace(" (TWh)", "")

        fig_gen = px.line(
            gen_melted,
            x="Year",
            y="TWh",
            color="Source",
            markers=True,
            color_discrete_map={
                "fossil fuels": "#8f3838",
                "renewables": "#2e7050",
                "nuclear": "#436a9c"
            }
        )
        fig_gen.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_gen, use_container_width=True)

    # Chart 3: National CO2 Emissions over time
    st.write("**3. National Carbon Emissions (Kilotonnes CO2)**")
    co2_data = country_df[["Year", "Value_co2_emissions_kt_by_country"]].dropna()
    if not co2_data.empty:
        fig_co2 = px.line(
            co2_data,
            x="Year",
            y="Value_co2_emissions_kt_by_country",
            markers=True
        )
        fig_co2.update_traces(line_color="#555555")
        fig_co2.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="kt CO2")
        st.plotly_chart(fig_co2, use_container_width=True)
