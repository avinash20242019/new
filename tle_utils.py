import requests

def fetch_tle(catnr: str):
    """
    Fetch the latest TLE for a given NORAD catalog number from CelesTrak.
    Returns: (line1, line2)
    """
    url = f"https://celestrak.com/satcat/tle.php?CATNR={catnr}"
    resp = requests.get(url)
    lines = resp.text.strip().splitlines()
    if len(lines) >= 2:
        return lines[-2], lines[-1]
    raise ValueError(f"Could not fetch TLE for CATNR={catnr}")
