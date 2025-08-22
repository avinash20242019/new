# GATI – Animated Satellite Orbits (TLE → 3D)

This app collects **TLE data for 10 satellites** and animates their motion around Earth for a chosen window (default ~1 month). It uses **Skyfield/SGP4** for propagation and **Plotly** for interactive 3D visualization inside **Streamlit**.

---

## Live Demo

👉 **Live Link:** _Add your deployed URL here_

_Recommended: Deploy to Streamlit Community Cloud (free) in minutes. Steps below._

---

## Approach (Short)

1. **Data**: Fetch the freshest TLE for each satellite from **Celestrak** via HTTP.
2. **Time Grid**: Build a uniform timeline over N days with a chosen timestep.
3. **Propagation**: Use **Skyfield (SGP4)** to propagate ECI/ECEF positions across the grid.
4. **Visualization**: Plot a semi-transparent Earth and 3D satellite markers + short orbital trails.
5. **Animation**: Create Plotly frames for each time step and control playback via Play/Pause buttons.

> Note: Using a single latest TLE over a month is primarily for visualization. For higher fidelity, update TLEs regularly or segment the timeline with daily/weekly TLE refreshes.

---

## Local Run

```bash
# 1) Create & activate a venv (optional, recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

---

## Change Satellites

Edit `satellites.json` (name → NORAD ID). Default list includes:

- ISS (ZARYA) – 25544
- Hubble Space Telescope – 20580
- NOAA 19 – 33591
- Terra – 25994
- Aqua – 27424
- Landsat 8 – 39084
- Sentinel-2A – 40697
- Sentinel-1A – 39634
- COSMO-SkyMed 1 – 31598
- Himawari-8 – 40267

> Tip: Keep a mix of LEO and GEO to see differing dynamics. GEO arcs may appear almost stationary in ECI but are interesting in ECEF.

---

## Deployment

### Option A: Streamlit Community Cloud (easiest)

1. Push this folder to a **public GitHub repo**.
2. Go to **share.streamlit.io** → "New app" → connect your repo.
3. Set **Main file** to `app.py` and **Python version** to 3.11+ (or default).
4. Add any **secrets** if you later secure Celestrak access (not required by default).
5. Once it builds, copy the URL and paste it above as your **Live Link**.

### Option B: Vercel (FastAPI wrapper)

Streamlit can run on Vercel, but it's simpler to wrap logic into a **FastAPI** app and serve a Plotly HTML.
If you prefer Vercel:

- Convert `app.py` into a FastAPI app that returns Plotly figures (or static HTML with embedded frames).
- Use a `vercel.json` with Python runtime.
- Ensure dependencies are listed in `requirements.txt`.

> If you want this path, I can generate a FastAPI version too.

---

## Notes & Improvements

- **Frame count vs. performance**: Long windows and small steps produce many frames. Tune in the sidebar.
- **Accuracy**: TLE-based SGP4 drifts far from truth beyond ~a few days; use frequent TLE refresh or higher-order force models for precision work.
- **ECI vs ECEF**: Currently visualized in **ECI** (non-rotating). Switch to **ECEF** for Earth-fixed visualization.
- **Collision Estimation**: Out of scope here, but you can compute pairwise distances per frame and flag close approaches.
- **Caching**: TLE calls are cached for an hour (`st.cache_data`).

---

## Tech

- Python, Streamlit, Plotly
- Skyfield, SGP4
- Requests, NumPy, Pandas

---

## License

MIT
