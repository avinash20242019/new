import json
from datetime import datetime, timezone
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from orbit_propagation import build_times, propagate_positions

st.set_page_config(page_title="GATI: 3D Satellite Orbits", layout="wide")
st.title("🛰️ GATI – Animated Satellite Orbits")
st.caption("Animates ~1 month of satellite orbits using local TLE data.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    days = st.slider("Days to simulate", 7, 35, 30)
    step = st.slider("Time step (minutes)", 5, 120, 30)
    start_date = st.date_input("Start date (UTC)", value=datetime.utcnow().date())
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    st.markdown("---")
    st.write("Edit `tle_data.json` to change satellites.")

# Load TLEs
with open("tle_data.json", "r") as f:
    tle_map_json = json.load(f)

tle_map_tuples = {name: tuple(lines) for name, lines in tle_map_json.items()}
names = list(tle_map_tuples.keys())
st.write(f"Tracking **{len(names)} satellites**: " + ", ".join(names))

# Time series & propagation
times = build_times(start_dt, days=days, step_minutes=step)
with st.spinner("Propagating orbits..."):
    results = propagate_positions(tle_map_tuples, times)

# Earth sphere
R_earth = 6371.0
phi = np.linspace(0, np.pi, 50)
theta = np.linspace(0, 2*np.pi, 100)
x = R_earth * np.outer(np.sin(phi), np.cos(theta))
y = R_earth * np.outer(np.sin(phi), np.sin(theta))
z = R_earth * np.outer(np.cos(phi), np.ones_like(theta))

fig = go.Figure()
fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.7, showscale=False, name="Earth"))

# Animation
frames = []
initial_data = []
symbols = ["circle", "square", "diamond", "cross", "x",
           "triangle-up", "triangle-down", "triangle-left", "triangle-right", "star"]
symbol_map = {name: symbols[i % len(symbols)] for i, name in enumerate(names)}
trail_frames = max(1, int(6*60/step))

for idx, name in enumerate(names):
    xyz = results[name]["eci_xyz"]
    initial_data.append(go.Scatter3d(x=[], y=[], z=[], mode="lines",
                                     name=f"{name} trail", line=dict(width=4), showlegend=False))
    initial_data.append(go.Scatter3d(x=[xyz[0,0]], y=[xyz[0,1]], z=[xyz[0,2]],
                                     mode="markers+text", name=name,
                                     marker=dict(size=4, symbol=symbol_map[name]),
                                     text=[name], textposition="top center"))

num_frames = len(times)
for k in range(num_frames):
    frame_data = []
    for name in names:
        xyz = results[name]["eci_xyz"]
        start_idx = max(0, k - trail_frames)
        trail = xyz[start_idx:k+1]
        frame_data.append(go.Scatter3d(x=trail[:,0], y=trail[:,1], z=trail[:,2],
                                       mode="lines", line=dict(width=4), showlegend=False))
        frame_data.append(go.Scatter3d(x=[xyz[k,0]], y=[xyz[k,1]], z=[xyz[k,2]],
                                       mode="markers+text", name=name,
                                       marker=dict(size=4, symbol=symbol_map[name]),
                                       text=[name], textposition="top center",
                                       showlegend=(k==0)))
    frames.append(go.Frame(data=frame_data, name=f"f{k}", traces=list(range(len(frame_data)))))

fig.add_traces(initial_data)
fig.update(frames=frames)
fig.update_layout(
    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False),
               zaxis=dict(visible=False), aspectmode="data"),
    margin=dict(l=0, r=0, t=40, b=0),
    title="Animated Orbits (ECI frame)",
    updatemenus=[dict(type="buttons", showactive=False, buttons=[
        dict(label="Play", method="animate",
             args=[None, {"frame": {"duration": 50, "redraw": False},
                          "fromcurrent": True, "transition": {"duration": 0}}]),
        dict(label="Pause", method="animate",
             args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
    ])],
    legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom")
)

st.plotly_chart(fig, use_container_width=True)
st.success("Done! Use the Play button to animate.")
