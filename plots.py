import plotly.graph_objects as go

def plot_anchor_plotly(layers_df, free_len, bond_len):
    fig = go.Figure()
    total_depth = free_len + bond_len
    
    # Calculate depths from elevations for plotting
    bottoms = layers_df['Elevation (m)'].tolist()
    tops = [0.0] + bottoms[:-1]
    
    max_plot_depth = max(bottoms[-1], total_depth + 2)

    # Plot Soil Layers
    for i, row in layers_df.iterrows():
        top = tops[i]
        bottom = bottoms[i]
        color = "bisque" if row['Soil Type'] == "Sand" else "darkseagreen"
        
        fig.add_shape(type="rect", x0=0, y0=top, x1=1, y1=bottom,
                      fillcolor=color, opacity=0.5, line_width=0)
        
        fig.add_annotation(x=0.5, y=(top + bottom) / 2, 
                           text=f"{row['Soil Type']} (N={row['SPT']})", showarrow=False)

    # Plot Anchor
    # Free Length (Blue)
    fig.add_trace(go.Scatter(x=[0.8, 0.8], y=[0, free_len], mode='lines',
                             line=dict(color='blue', width=4), name='Free Length'))
    
    # Bond Length (Red)
    fig.add_trace(go.Scatter(x=[0.8, 0.8], y=[free_len, total_depth], mode='lines',
                             line=dict(color='red', width=12), name='Bond Length'))

    fig.update_layout(
        title="Ground Anchor Soil Profile",
        yaxis_range=[max_plot_depth, 0], # Inverted for depth
        xaxis_visible=False,
        template="plotly_white",
        height=700,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig