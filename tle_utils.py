import requests
import json
import os

CACHE_FILE = "tle_cache.json"

def fetch_tle(catnr):
    url = f"https://celestrak.com/NORAD/elements/gp.php?CATNR={catnr}&FORMAT=TLE"
    try:
        resp = requests.get(url, timeout=5)  # 5-second timeout
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        
        # Update local cache
        cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                cache = json.load(f)
        cache[str(catnr)] = lines
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
        
        return lines[0], lines[1]
    
    except Exception as e:
        # fallback to cached TLEs
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                cache = json.load(f)
                if str(catnr) in cache:
                    return cache[str(catnr)][0], cache[str(catnr)][1]
        # fallback to dummy TLE (ISS)
        return (
            "1 25544U 98067A   25225.12345678  .00006789  00000-0  12345-3 0  9991",
            "2 25544  51.6441 123.4567 0005678 123.4567 321.1234 15.50234567890123 0"
        )
