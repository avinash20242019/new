from typing import Dict, List, Tuple
import numpy as np
from skyfield.api import Loader, EarthSatellite
from datetime import datetime, timedelta

# Load Skyfield data
load = Loader(".skyfield_data")

def build_times(start: datetime, days: int, step_minutes: int) -> List[datetime]:
    """Generate a list of datetime objects from start, over a number of days, at given minute intervals."""
    times = []
    t = start
    end = start + timedelta(days=days)
    while t <= end:
        times.append(t)
        t += timedelta(minutes=step_minutes)
    return times

def propagate_positions(tle_map: Dict[str, Tuple[str, str]], times: List[datetime]):
    """
    Propagate satellite positions from TLEs.

    Returns:
        dict: name -> {
            time_list: list of datetime,
            eci_xyz: np.array of shape (N, 3) in km,
            ecef_xyz: np.array of shape (N, 3) in km
        }
    """
    ts = load.timescale()
    results = {}
    sky_times = ts.from_datetimes(times)

    for name, (l1, l2) in tle_map.items():
        sat = EarthSatellite(l1, l2, name, ts)
        geocentric = sat.at(sky_times)

        # ECI positions
        eci_x, eci_y, eci_z = geocentric.position.km
        eci = np.vstack([eci_x, eci_y, eci_z]).T

        # ECEF positions (modern Skyfield API)
        itrs = geocentric.itrs_xyz()  # ✅ returns (x, y, z) in meters
               # ✅ use this
        ecef_x, ecef_y, ecef_z = itrs.position.km
        ecef = np.vstack([ecef_x, ecef_y, ecef_z]).T

        results[name] = dict(
            time_list=times,
            eci_xyz=eci,
            ecef_xyz=ecef
        )

    return results

