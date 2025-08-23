# orbit_propagation.py
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import numpy as np
from sgp4.api import Satrec, jday

def build_times(start: datetime, days: int, step_minutes: int) -> List[datetime]:
    times = []
    t = start
    end = start + timedelta(days=days)
    while t <= end:
        times.append(t)
        t += timedelta(minutes=step_minutes)
    return times

def propagate_positions(tle_map: Dict[str, Tuple[str, str, str]], times: List[datetime]):
    """
    Propagate satellite positions from TLEs using SGP4.
    
    Returns:
        dict: name -> {
            time_list: list of datetime,
            eci_xyz: np.array of shape (N,3) in km
        }
    """
    results = {}
    for name, (title, l1, l2) in tle_map.items():
        sat = Satrec.twoline2rv(l1, l2)
        eci_list = []

        for t in times:
            jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
            e, r, v = sat.sgp4(jd, fr)
            if e == 0:
                eci_list.append([r[0], r[1], r[2]])  # km
            else:
                eci_list.append([None, None, None])

        results[name] = dict(
            time_list=times,
            eci_xyz=np.array(eci_list)
        )

    return results
