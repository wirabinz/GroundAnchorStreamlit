import plotly.graph_objects as go
import numpy as np

def plot_anchor_plotly(layers_df, free_l, bond_l, anchor_elev, angle_deg):
    fig = go.Figure()
    
    # 1. Setup Trigonometry
    angle_rad = np.radians(angle_deg)
    
    # 2. Coordinate Calculations
    # Start Point (Top of Free Length)
    x0, y0 = 0, anchor_elev
    
    # End of Free Length / Start of Bond
    x1 = free_l * np.cos(angle_rad)
    y1 = anchor_elev + (free_l * np.sin(angle_rad))
    
    # End of Bond Length
    x2 = (free_l + bond_l) * np.cos(angle_rad)
    y2 = anchor_elev + ((free_l + bond_l) * np.sin(angle_rad))
    
    # 3. Dynamic Axis Range Logic
    if angle_deg == 90:
        # For vertical anchors, center the anchor at x=0 with a symmetrical buffer
        x_min, x_max = -2, 2
    else:
        # For inclined anchors, start at 0 and go to the right with a buffer
        x_min, x_max = 0, max(x2 + 2, 5)

    # 4. Soil Stratigraphy (Background)
    bottoms = layers_df['Elevation (m)'].tolist()
    tops = [0.0] + bottoms[:-1]
    max_depth = max(bottoms[-1], y2 + 2)

    for i, row in layers_df.iterrows():
        top = tops[i]
        bottom = bottoms[i]
        color = "bisque" if row['Soil Type'] == "Sand" else "darkseagreen"
        
        # Extend the soil rectangles to fill the dynamic X range
        fig.add_shape(type="rect", x0=x_min, y0=top, x1=x_max, y1=bottom,
                      fillcolor=color, opacity=0.3, line_width=0, layer="below")
        
        # Position label on the far right of the current view
        fig.add_annotation(x=x_max * 0.85, y=(top + bottom) / 2, 
                           text=f"{row['Soil Type']}", showarrow=False, 
                           font=dict(size=12, color="gray"))

    # 5. Plot Anchor Segments
    # Free Length
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines+markers',
                             line=dict(color='blue', width=3, dash='dash'), 
                             name='Free Length'))
    
    # Bond Length
    fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines+markers',
                             line=dict(color='red', width=8), 
                             name='Bond Length'))

    # 6. Figure Layout
    fig.update_layout(
        title=f"Ground Anchor Profile (Angle: {angle_deg}°)",
        yaxis_range=[max_depth, 0], # Inverted for depth
        xaxis_range=[x_min, x_max],
        xaxis_title="Horizontal Distance (m)",
        yaxis_title="Depth (m)",
        template="plotly_white",
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig