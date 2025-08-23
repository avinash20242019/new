from typing import Dict, List, Tuple
import numpy as np
from skyfield.api import Loader, EarthSatellite
from datetime import datetime, timedelta

load = Loader(".skyfield_data")

def build_times(start: datetime, days: int, step_minutes: int) -> List[datetime]:
    """Generate a list of datetime objects from start over a number of days at given intervals."""
    times = []
    t = start
    end = start + timedelta(days=days)
    while t <= end:
        times.append(t)
        t += timedelta(minutes=step_minutes)
    return times

def propagate_positions(tle_map: Dict[str, Tuple[str, str]], times: List[datetime]):
    """Propagate satellite positions from TLEs using frame_xyz('itrs') for ECEF."""
    ts = load.timescale()
    results = {}

    for name, (l1, l2) in tle_map.items():
        sat = EarthSatellite(l1, l2, name, ts)
        eci_list = []
        ecef_list = []

        for t in times:
            # Single-time Skyfield Time
            sky_t = ts.utc(t.year, t.month, t.day, t.hour, t.minute, t.second)
            geocentric = sat.at(sky_t)  # single-time Geocentric

            # ECI positions in km
            eci_list.append(geocentric.positi_
