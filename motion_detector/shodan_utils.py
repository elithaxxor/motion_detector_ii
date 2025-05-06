import os
import requests

SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

SHODAN_BASE_URL = "https://api.shodan.io"

def shodan_search(query, facets=None, page=1):
    """
    Search Shodan for a query string.
    Returns JSON results or raises Exception.
    """
    if not SHODAN_API_KEY:
        raise ValueError("SHODAN_API_KEY not set in environment.")
    params = {
        'key': SHODAN_API_KEY,
        'query': query,
        'page': page
    }
    if facets:
        params['facets'] = facets
    resp = requests.get(f"{SHODAN_BASE_URL}/shodan/host/search", params=params)
    resp.raise_for_status()
    return resp.json()

def shodan_host(ip):
    """
    Get all available information for an IP address from Shodan.
    Returns JSON results or raises Exception.
    """
    if not SHODAN_API_KEY:
        raise ValueError("SHODAN_API_KEY not set in environment.")
    params = {'key': SHODAN_API_KEY}
    resp = requests.get(f"{SHODAN_BASE_URL}/shodan/host/{ip}", params=params)
    resp.raise_for_status()
    return resp.json()
