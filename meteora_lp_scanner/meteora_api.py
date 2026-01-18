import requests

BASE_URL = "https://dlmm-api.meteora.ag"


def fetch_all_pairs(timeout=30):
    url = f"{BASE_URL}/pair/all"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()
