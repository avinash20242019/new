
import requests
from typing import Tuple, List

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={catnr}&FORMAT=TLE"

def fetch_tle(catnr: int) -> Tuple[str, str]:
    """
    Fetches TLE lines (L1, L2) for a given NORAD catalog number from Celestrak.
    Returns (line1, line2). Raises on HTTP errors.
    """
    url = CELESTRAK_URL.format(catnr=catnr)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    lines = [ln.strip() for ln in resp.text.splitlines() if ln.strip()]
    # Celestrak returns name line followed by 2 TLE lines
    # We find the first line that starts with '1 ' and '2 '
    l1, l2 = None, None
    for i, ln in enumerate(lines):
        if ln.startswith("1 "):
            l1 = ln
            if i + 1 < len(lines) and lines[i+1].startswith("2 "):
                l2 = lines[i+1]
                break
    if not l1 or not l2:
        raise ValueError("Could not parse TLE from response for CATNR={}".format(catnr))
    return l1, l2
