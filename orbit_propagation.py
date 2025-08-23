from typing import Dict, List, Tuple
import numpy as np
from skyfield.api import Loader, EarthSatellite
from datetime import datetime, timedelta

# Load Skyfield data
load = Loader(".skyfield_data")

def build_times(start: datetime, days: int, step_minutes: int) -> List[datetime]:
    """
    Generate a list of datetime objects from start, over a number of days,
    at given minute intervals.
    """
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
            geocentric = sat.at(sky_t)

            # ECI positions in km
            eci_x, eci_y, eci_z = geocentric.position.km
            eci_list.append([eci_x, eci_y, eci_z])

            # ECEF positions in km using modern Skyfield
            x_m, y_m, z_m = geocentric.itrs_xyz()  # meters
            ecef_list.append([x_m/1000, y_m/1000, z_m/1000])  # km

        results[name] = dict(
            time_list=times,
            eci_xyz=np.array(eci_list),
            ecef_xyz=np.array(ecef_list)
        )

    return results

