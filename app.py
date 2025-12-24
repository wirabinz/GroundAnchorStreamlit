import streamlit as st
import pandas as pd
import numpy as np
import formulas
import plots

st.set_page_config(layout="wide", page_title="Ground Anchor Analysis")

# --- NAVIGATION ---
page = st.sidebar.selectbox("Select Page", ["Main Analysis", "Documentation"])

def benchmark_page():
    st.title("📚 Bond Strength & Design Benchmark Reference")
    st.markdown("""
    This page serves as a technical reference for the calculations performed in this application, 
    based on **Michel Bustamante (1985)** : Une méthode pour le calcul des tirants et des micropieux injectés.
    """)

    # --- SECTION 1: CALCULATION THEORY ---
    st.header("1. Ultimate Tensile Load ($T_L$)")
    st.markdown(r"""
    When the bonded length ($L_s$) of an anchor extends across several soil layers, the total ultimate capacity 
    is the summation of the individual layer capacities:
    """)
    
    # LaTeX Formula for TL
    st.latex(r"T_L = \sum_{i} \pi \cdot D_{si} \cdot q_{si} \cdot l_{si}")

    
    
    st.markdown("""
    **Where:**
    * $T_L$: Ultimate tensile load of the isolated anchor.
    * $D_{si}$: Average diameter of the grout bulb in layer $i$.
    * $q_{si}$: Ultimate unit lateral friction (bond strength) for layer $i$.
    * $l_{si}$: Length of the bulb bonded within layer $i$.
    """)


    # Attach the image here
    st.image("anchor-sketch.png", caption="Schematic representation of a tie rod grouted in a multilayer soil profile.", width=450)
    st.divider()

    # --- SECTION 2: ENLARGEMENT COEFFICIENT ---
    st.header("2. Grout Bulb Diameter & Enlargement Coefficient (α)")
    st.markdown(r"""
    The actual diameter of the grout bulb ($D_s$) is typically larger than the drilled borehole diameter ($D_d$) 
    due to high-pressure injection. This is calculated using the enlargement coefficient:
    """)
    
    st.latex(r"D_s = \alpha \cdot D_d")

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("Typical Values for α")
        alpha_data = {
            "Soil Type": [
                "Gravel", "Sandy gravel", "Gravelly sand", 
                "Coarse / Medium / Fine / Silty sand", "Silt", "Clay", 
                "Marl / Marly limestone", "Altered or fragmented rock"
            ],
            "Coefficient α": ["1.3 - 1.4", "1.2 - 1.4", "1.2 - 1.3", "1.1 - 1.2", "1.1 - 1.2", "1.2", "1.1 - 1.2", "1.1"]
        }
        st.table(pd.DataFrame(alpha_data))

    with col_b:
        st.info("""
        **Application Tip:** In the 'Geometry' input section of this app, the **Borehole Enlargement Coefficient** defaults to 1.0 (theoretical). Adjust this based on the soil types in your stratigraphy 
        using the table on the left to get a more realistic capacity estimate.
        """)

    st.divider()

    # --- SECTION 3: GRAPHS ---
    st.header("3. Bond Strength Benchmarks ($q_s$)")
    
    graph_col1, graph_col2 = st.columns(2)
    
    with graph_col1:
        st.plotly_chart(plots.plot_granular_benchmark(), use_container_width=True)
        st.plotly_chart(plots.plot_comparison_benchmark(100), use_container_width=True)

    with graph_col2:
        st.plotly_chart(plots.plot_clay_benchmark(), use_container_width=True)
        st.plotly_chart(plots.plot_comparison_benchmark(30), use_container_width=True)

    st.divider()

    # --- SECTION 4: CROSSOVER SUMMARY ---
    st.subheader("🎯 Engineering Insights: The Crossover Point")
    st.success("""
    * **Clay Advantage:** In soft soils with **SPT < 41**, Clay typically provides a higher bond strength than Sand for the same N-value.
    * **Sand Advantage:** In denser soils where **SPT > 41**, the linear growth of Sand bond strength (0.005 x N) overtakes the piecewise growth characteristic of Clay.
    * **Critical Value:** At approximately **SPT 41.25**, the two models intersect at a bond strength of ~0.206 MPa.
    """)

if page == "Documentation":
    benchmark_page()

else:
    st.title("📊 Ground Anchor Ultimate Bond Strength Analysis")

    # --- Mode Selection ---
    analysis_mode = st.sidebar.radio(
        "Select Analysis Mode",
        [
            "Check Capacity (Fixed Length & SF)", 
            "Design Mode (Find Required Length)",
            "Safety Check (Find Actual SF)"
        ]
    )

    with st.form("anchor_form"):
        top_col1, top_col2, top_col3 = st.columns(3)

        with top_col1:
            st.subheader("1. Geometry")
            dia_mm = st.number_input("Borehole Diameter (mm)", min_value=50.0, value=150.0, step=10.0)
            enlarge_coeff = st.number_input("Borehole Enlargement Coefficient", min_value=1.0, value=1.0, step=0.1)
            anchor_elev = st.number_input("Anchor Elevation (m)", value=0.0)
            angle_deg = st.number_input("Angle of Inclination (deg)", min_value=1.0, max_value=90.0, value=45.0)

        with top_col2:
            st.subheader("2. Length Configurations")
            free_l = st.number_input("Free Length (m)", min_value=1.0, value=5.0)

            if free_l < 4.5:
                st.warning("⚠️ **SNI 8460:2017 Warning**: Minimum free length should be 4.5m.")

            if analysis_mode == "Design Mode (Find Required Length)":
                st.info("💡 Bond Length will be calculated based on the Design Load.")
                bond_l_input = 0.0 
            else:
                bond_l_input = st.number_input("Bond Length (m)", min_value=1.0, value=10.0)
                if bond_l_input > 13.0:
                    st.warning("⚠️ **SNI 8460:2017 Warning**: Bond length > 13m requires on-site pullout test.")

        with top_col3:
            st.subheader("3. Design Load & SF")
            design_load = st.number_input("Designated Load (Tons)", min_value=0.1, value=30.0)

            if analysis_mode == "Safety Check (Find Actual SF)":
                st.info("💡 Factor of Safety will be calculated based on the Bond Length.")
                fos_input = 1.0 
            else:
                fos_input = st.number_input("Factor of Safety (SF)", min_value=1.0, value=3.0, step=0.1)

        st.divider()
        st.subheader("4. Soil Stratigraphy")
        init_data = pd.DataFrame([
            {"Elevation (m)": 8.0, "Soil Type": "Clay", "SPT": 25.0},
            {"Elevation (m)": 20.0, "Soil Type": "Sand", "SPT": 25.0},
        ])

        soil_data = st.data_editor(
            init_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Soil Type": st.column_config.SelectboxColumn("Soil Type", options=["Clay", "Sand"], required=True),
                "SPT": st.column_config.NumberColumn("SPT Value", min_value=1),
                "Elevation (m)": st.column_config.NumberColumn("Bottom Elevation (m)", min_value=0.1)
            }
        )
        submit_btn = st.form_submit_button("Run Analysis", use_container_width=True)

    if submit_btn:
        angle_rad = np.radians(angle_deg)
        sin_theta = np.sin(angle_rad)
        effective_dia_cm = (dia_mm * enlarge_coeff) / 10.0
        conv_mpa_to_kg = 10.1971621
        max_soil_depth = soil_data['Elevation (m)'].max()

        final_bond_l = bond_l_input
        final_fos = fos_input
        error_flag = False

        # --- Mode 2 Logic: Design Mode ---
        if analysis_mode == "Design Mode (Find Required Length)":
            current_bond_l = 0.5
            found = False
            while current_bond_l <= 100.0:
                temp_ult_cap = 0.0
                z_s = anchor_elev + (free_l * sin_theta)
                z_e = anchor_elev + ((free_l + current_bond_l) * sin_theta)

                if z_e > max_soil_depth:
                    st.error(f"❌ **Insufficient Soil Data**: Depth reached {max_soil_depth}m without meeting capacity.")
                    error_flag = True
                    break
                
                tops = [0.0] + soil_data['Elevation (m)'].tolist()[:-1]
                for i, row in soil_data.iterrows():
                    z_ov = max(0.0, min(z_e, row['Elevation (m)']) - max(z_s, tops[i]))
                    if z_ov > 0:
                        qs = (formulas.calculate_clay_bond_strength(row['SPT']) if row['Soil Type']=="Clay" else formulas.calculate_sand_bond_strength(row['SPT'])) * conv_mpa_to_kg
                        temp_ult_cap += (qs * (np.pi * effective_dia_cm * (z_ov/sin_theta) * 100.0)) / 1000.0

                if (temp_ult_cap / final_fos) >= design_load:
                    final_bond_l = current_bond_l
                    found = True
                    break
                current_bond_l += 0.1

            if found and final_bond_l > 13.0:
                st.warning("⚠️ **SNI 8460:2017 Warning**: Calculated Bond length > 13m requires on-site pullout test.")

        # --- Mode 1 & 3 Logic (Fixed Bond Length) ---
        else:
            z_s = anchor_elev + (free_l * sin_theta)
            z_e = anchor_elev + ((free_l + final_bond_l) * sin_theta)

            if z_e > max_soil_depth:
                st.error(f"❌ **Error**: Anchor tip ({z_e:.2f}m) exceeds defined soil depth ({max_soil_depth}m).")
                error_flag = True

            if analysis_mode == "Safety Check (Find Actual SF)":
                total_ult_capacity = 0.0
                tops = [0.0] + soil_data['Elevation (m)'].tolist()[:-1]
                for i, row in soil_data.iterrows():
                    z_ov = max(0.0, min(z_e, row['Elevation (m)']) - max(z_s, tops[i]))
                    if z_ov > 0:
                        qs = (formulas.calculate_clay_bond_strength(row['SPT']) if row['Soil Type']=="Clay" else formulas.calculate_sand_bond_strength(row['SPT'])) * conv_mpa_to_kg
                        total_ult_capacity += (qs * (np.pi * effective_dia_cm * (z_ov/sin_theta) * 100.0)) / 1000.0
                final_fos = total_ult_capacity / design_load

        # --- Final Result Assembly ---
        if not error_flag:
            z_bond_start = anchor_elev + (free_l * sin_theta)
            z_bond_end = anchor_elev + ((free_l + final_bond_l) * sin_theta)
            results_raw = []
            total_working_capacity = 0.0
            tops = [0.0] + soil_data['Elevation (m)'].tolist()[:-1]

            for i, row in soil_data.iterrows():
                z_overlap = max(0.0, min(z_bond_end, row['Elevation (m)']) - max(z_bond_start, tops[i]))
                if z_overlap > 0:
                    # SNI SPT Check
                    if row['Soil Type'] == "Sand" and row['SPT'] < 25:
                        st.error(f"❌ **SNI Violation**: Sand at {tops[i]}m-{row['Elevation (m)']}m has SPT < 25.")
                    if row['Soil Type'] == "Clay" and row['SPT'] < 20:
                        st.error(f"❌ **SNI Violation**: Clay at {tops[i]}m-{row['Elevation (m)']}m has SPT < 20.")

                    act_l = z_overlap / sin_theta
                    qs_ult = (formulas.calculate_clay_bond_strength(row['SPT']) if row['Soil Type']=="Clay" else formulas.calculate_sand_bond_strength(row['SPT'])) * conv_mpa_to_kg
                    qs_work = qs_ult / final_fos
                    cap = (qs_work * (np.pi * effective_dia_cm * act_l * 100.0)) / 1000.0
                    total_working_capacity += cap

                    results_raw.append({
                        "Range": f"{tops[i]}m - {row['Elevation (m)']}m",
                        "Soil Thickness (m)": round(z_overlap, 2), "Bond Length (m)": round(act_l, 2),
                        "Type": row['Soil Type'], "Ultimate Bond Stress (kg/cm²)": round(qs_ult, 4),
                        "Working Bond Stress (kg/cm²)": round(qs_work, 4), "Working Capacity (Tons)": round(cap, 2)
                    })

            if results_raw:
                out_col1, out_col2 = st.columns([1, 1])
                with out_col1:
                    st.plotly_chart(plots.plot_anchor_plotly(soil_data, free_l, final_bond_l, anchor_elev, angle_deg), use_container_width=True)
                with out_col2:
                    st.subheader("Calculation Summary")
                    st.info(f"📍 **Top of Bond Elevation:** {z_bond_start:.2f} m")
                    st.table(pd.DataFrame(results_raw).set_index("Range").T)
                    st.divider()
                    st.subheader("Design Verification")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Designated Load", f"{design_load:.2f} Tons")

                    # --- Mode Specific Metrics ---
                    if analysis_mode == "Design Mode (Find Required Length)":
                        # Highlight the calculated lengths
                        c2.metric("Required Bond Length", f"{final_bond_l:.2f} m")
                        c3.metric("Total Anchor Length", f"{free_l + final_bond_l:.2f} m")
                        st.success(f"✅ **SUCCESS**: A bond length of **{final_bond_l:.2f} m** is required to satisfy the load with an SF of {final_fos}.")

                    elif analysis_mode == "Safety Check (Find Actual SF)":
                        c2.metric("Computed Safety Factor (SF)", f"{final_fos:.2f}")
                        c3.metric("Bond Length Used", f"{final_bond_l:.2f} m")

                    else: # Check Capacity
                        c2.metric("Working Capacity", f"{total_working_capacity:.2f} Tons")
                        c3.metric("Factor of Safety", f"{final_fos:.2f}")
                        if total_working_capacity >= design_load:
                            st.success(f"✅ **PASS**: Working Capacity exceeds Design Load.")
                        else:
                            st.error(f"❌ **FAIL**: Insufficient Capacity.")

        st.divider()
        st.markdown("""
        **Calculation References:**
        1. **SNI 8460:2017** - *Persyaratan Perancangan Geoteknik.*
        2. **Bustamante, M. (1985)** - *Une méthode pour le calcul des tirants et des micropieux injectés.*
        """)