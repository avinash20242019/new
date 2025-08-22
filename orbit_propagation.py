
from typing import Dict, List, Tuple
import numpy as np
from skyfield.api import Loader, EarthSatellite
from datetime import datetime, timedelta, timezone

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
    """
    For each satellite name -> (L1, L2), returns dict of:
      name -> dict(time_list=[...], ecef_xyz=np.array[[x,y,z],...], eci_xyz=np.array[[x,y,z],...])
    Units: kilometers
    """
    ts = load.timescale()
    results = {}
    # Convert datetimes to Skyfield times once
    sky_times = ts.from_datetimes(times)
    for name, (l1, l2) in tle_map.items():
        sat = EarthSatellite(l1, l2, name, ts)
        # Observed in ITRS (ECEF) via wgs84; and also GCRS (ECI-ish) positions via .at().position.km
        geocentric = sat.at(sky_times)
        eci_x, eci_y, eci_z = geocentric.position.km  # ECI-like
        eci = np.vstack([eci_x, eci_y, eci_z]).T

        # ECEF for drawing relative to rotating Earth (optional)
        itrs = geocentric.itrs_xyz.km  # x,y,z in ECEF
        ecef = np.vstack(itrs).T

        results[name] = dict(
            time_list=times,
            eci_xyz=eci,
            ecef_xyz=ecef
        )
    return results
