from typing import Dict, List, Tuple
import numpy as np
from skyfield.api import Loader, EarthSatellite
from datetime import datetime, timedelta

load = Loader(".skyfield_data")

def build_times(start: datetime, days: int, step_minutes: int) -> List[datetime]:
    times = []
    t = start
    end = start + timedelta(days=days)
    while t <= end:
        times.append(t)
        t += timedelta(minutes=step_minutes)
    return times

def propagate_positions(tle_map: Dict[str, Tuple[str, str]], times: List[datetime]):
    ts = load.timescale()
    results = {}

    for name, (l1, l2) in tle_map.items():
        sat = EarthSatellite(l1, l2, name, ts)
        eci_list = []
        ecef_list = []

        for t in times:
            sky_t = ts.utc(t.year, t.month, t.day, t.hour, t.minute, t.second)
            geocentric = sat.at(sky_t)  # single-time Geocentric

            # ECI in km
            eci_list.append(geocentric.position.km)

            # ECEF in km
            itrs = geocentric.itrs()  # single-time ECEF
            pos_m = itrs.position.m
            ecef_list.append([pos_m[0]/1000, pos_m[1]/1000, pos_m[2]/1000])

        results[name] = dict(
            time_list=times,
            eci_xyz=np.array(eci_list),
            ecef_xyz=np.array(ecef_list)
        )

    return results
