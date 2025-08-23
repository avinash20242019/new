# app.py
import json
from datetime import datetime, timedelta, timezone
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import requests
from sgp4.api import Satrec, jday

st.set_page_config(page_title="GATI: 3D Satellite Orbits", layout="wide")
st.title("🛰️ GATI – Animated Satellite Orbits")
st.caption("Fetches TLEs and animates ~1 month of orbital motion in 3D.")

# --- Sidebar configuration ---
with st.sidebar:
    st.header("Configuration")
    days = st.slider("Days to simulate", 7, 35, 30)
    step = st.slider("Time step (minutes)", 5, 120, 30)
    start_date = st.date_input("Start date (UTC)", value=datetime.utcnow().date())
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    st.markdown("---")
    st.write("Edit `satellites.json` to change tracked satellites.")

# --- Load satellites ---
with open("satellites.json", "r") as f:
    sats = json.load(f)

names = list(sats.keys())
st.write(f"Tracking **{len(names)} satellites**: " + ", ".join(names))

# --- Fetch TLEs ---
@st.cache_data(ttl=3600)
def fetch_tle(catnr):
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={catnr}&FORMAT=TLE"
    resp = requests.get(url)
    lines = resp.text.strip().split("\n")
    if len(lines) < 3:
        raise ValueError(f"TLE not found for CATNR {catnr}")
    return lines[0], lines[1], lines[2]

@st.cache_data(ttl=3600)
def get_tles(catnrs):
    tle_map = {}
    for name, catnr in catnrs.items():
        tle_map[name] = fetch_tle(catnr)
    return tle_map

with st.spinner("Fetching latest TLEs..."):
    tle_map = get_tles(sats)

# --- Build time series ---
def build_times(start, days, step_minutes):
    times = []
    t = start
    end = start + timedelta(days=days)
    while t <= end:
        times.append(t)
        t += timedelta(minutes=step_minutes)
    return times

times = build_times(start_dt, days=days, step_minutes=step)

# --- Propagate satellites using SGP4 ---
@st.cache_data
def propagate_positions(tle_map, times):
    results = {}
    for name, (l0, l1, l2) in tle_map.items():
        sat = Satrec.twoline2rv(l1, l2)
        eci_list = []

        for t in times:
            jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
            e, r, v = sat.sgp4(jd, fr)
            if e == 0:
                eci_list.append([r[0], r[1], r[2]])  # km
            else:
                eci_list.append([None, None, None])

        results[name] = dict(time_list=times, eci_xyz=np.array(eci_list))
    return results

with st.spinner("Propagating orbits..."):
    results = propagate_positions(tle_map, times)

# --- Build Earth sphere ---
R_earth = 6371.0
phi = np.linspace(0, np.pi, 50)
theta = np.linspace(0, 2*np.pi, 100)
x = R_earth * np.outer(np.sin(phi), np.cos(theta))
y = R_earth * np.outer(np.sin(phi), np.sin(theta))
z = R_earth * np.outer(np.cos(phi), np.ones_like(theta))

fig = go.Figure()
fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.7, showscale=False, name="Earth"))

# --- Animation setup ---
frames = []
initial_data = []
symbols = ["circle", "square", "diamond", "cross", "x", "triangle-up", "triangle-down", "triangle-left", "triangle-right", "star"]
symbol_map = {name: symbols[i % len(symbols)] for i, name in enumerate(names)}
trail_frames = max(1, int(6*60/step))

for idx, name in enumerate(names):
    xyz = results[name]["eci_xyz"]
    initial_data.append(go.Scatter3d(x=[], y=[], z=[], mode="lines", name=f"{name} trail", line=dict(width=4), showlegend=False))
    initial_data.append(go.Scatter3d(x=[xyz[0,0]], y=[xyz[0,1]], z=[xyz[0,2]], mode="markers+text", name=name,
                                     marker=dict(size=4, symbol=symbol_map[name]), text=[name], textposition="top center"))

num_frames = len(times)
for k in range(num_frames):
    frame_data = []
    for name in names:
        xyz = results[name]["eci_xyz"]
        start_idx = max(0, k - trail_frames)
        trail = xyz[start_idx:k+1]
        frame_data.append(go.Scatter3d(x=trail[:,0], y=trail[:,1], z=trail[:,2], mode="lines", line=dict(width=4), showlegend=False))
        frame_data.append(go.Scatter3d(x=[xyz[k,0]], y=[xyz[k,1]], z=[xyz[k,2]], mode="markers+text", name=name,
                                       marker=dict(size=4, symbol=symbol_map[name]), text=[name], textposition="top center",
                                       showlegend=(k==0)))
    frames.append(go.Frame(data=frame_data, name=f"f{k}", traces=list(range(len(frame_data)))))

fig.add_traces(initial_data)
fig.update(frames=frames)
fig.update_layout(
    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode="data"),
    margin=dict(l=0, r=0, t=40, b=0),
    title="Animated Orbits (ECI frame)",
    updatemenus=[dict(type="buttons", showactive=False, buttons=[
        dict(label="Play", method="animate", args=[None, {"frame": {"duration": 50, "redraw": False}, "fromcurrent": True, "transition": {"duration": 0}}]),
        dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
    ])],
    legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom")
)

st.plotly_chart(fig, use_container_width=True)
st.success("Done! Use the Play button to animate.")
