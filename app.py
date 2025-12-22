import streamlit as st
import pandas as pd
import numpy as np
import formulas
import plots

st.set_page_config(layout="wide", page_title="Ground Anchor Analysis")
st.title("🏗️ Ground Anchor Ultimate Bond Strength Analysis")

# Main Input Form
with st.form("anchor_form"):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Geometry")
        dia_mm = st.number_input("Borehole Diameter (mm)", min_value=50.0, value=150.0, step=10.0)
        free_l = st.number_input("Free Length (m)", min_value=1.0, value=5.0)
        bond_l = st.number_input("Bond Length (m)", min_value=1.0, value=10.0)
        
    with col2:
        st.subheader("2. Soil Stratigraphy")
        st.caption("Input the bottom elevation for each layer. Top of Layer 1 is assumed to be 0.0.")
        
        # Initial DataFrame structure
        init_data = pd.DataFrame([
            {"Elevation (m)": 8.0, "Soil Type": "Clay", "SPT": 10.0},
            {"Elevation (m)": 20.0, "Soil Type": "Sand", "SPT": 30.0},
        ])
        
        soil_data = st.data_editor(
            init_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Soil Type": st.column_config.SelectboxColumn(
                    "Soil Type",
                    options=["Clay", "Sand"],
                    required=True,
                ),
                "SPT": st.column_config.NumberColumn(
                    "SPT Value",
                    min_value=1,
                    format="%d",
                    required=True,
                ),
                "Elevation (m)": st.column_config.NumberColumn(
                    "Bottom Elevation (m)",
                    min_value=0.1,
                    required=True,
                )
            }
        )
    
    submit_btn = st.form_submit_button("Run Analysis")

if submit_btn:
    # 1. Processing Elevations into Top/Bottom pairs
    bottoms = soil_data['Elevation (m)'].tolist()
    tops = [0.0] + bottoms[:-1]
    
    # 2. Calculation setup
    anchor_top = free_l
    anchor_bot = free_l + bond_l
    conv_mpa_to_kg = 10.1971621 # Conversion factor from notebook
    
    results_raw = []
    total_capacity = 0.0
    
    for i, row in soil_data.iterrows():
        top = tops[i]
        bottom = bottoms[i]
        spt = row['SPT']
        soil_type = row['Soil Type']
        
        # Calculate intersection with bond length
        overlap = max(0.0, min(anchor_bot, bottom) - max(anchor_top, top))
        
        if overlap > 0:
            # Determine MPa based on soil type logic
            if soil_type == "Clay":
                qs_mpa = formulas.calculate_clay_bond_strength(spt)
            else:
                qs_mpa = formulas.calculate_sand_bond_strength(spt)
                
            qs_kg = qs_mpa * conv_mpa_to_kg
            area_cm2 = (dia_mm / 10.0) * np.pi * (overlap * 100.0)
            capacity_tons = (qs_kg * area_cm2) / 1000.0
            
            total_capacity += capacity_tons
            
            # UPDATED: Added "Thickness (m)" to the dictionary
            results_raw.append({
                "Range": f"{top}m - {bottom}m", # Top-left column title set here
                "Soil Thickness (m)": round(overlap, 2), # New row added
                "Type": soil_type,
                "SPT": spt,
                "Bond Stress (kg/cm²)": round(qs_kg, 4),
                "Capacity (Tons)": round(capacity_tons, 2)
            })

    # 3. Output Display
    if not results_raw:
        st.error("Error: The anchor bond length does not intersect with the defined soil layers.")
    else:
        out_col1, out_col2 = st.columns([1, 1])
        
        with out_col1:
            st.plotly_chart(plots.plot_anchor_plotly(soil_data, free_l, bond_l), use_container_width=True)
            
        with out_col2:
            st.subheader("Calculation Summary")
            
            # UPDATED: Set 'Range' as index so it becomes the top-left header after transpose (.T)
            summary_df = pd.DataFrame(results_raw).set_index("Range").T
            st.table(summary_df)
            
            st.metric("Total Anchor Working Capacity", f"{total_capacity:.2f} Tons")