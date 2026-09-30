import os
import requests
import pandas as pd

BASE_URL=os.getenv("EIA_BASE_URL","https://api.eia.gov/v2")

def fetch_eia(endpoint,params):
    api_key=os.getenv("EIA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "EIA_API_KEY is not set. Get an EIA API key before using this module."
        )

    url=endpoint if endpoint.startswith("http") else (
        f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    )
    params=dict(params)
    params["api_key"]=api_key

    response=requests.get(url,params=params,timeout=60)
    response.raise_for_status()

    payload=response.json()
    return pd.DataFrame(payload.get("response",{}).get("data",[]))

def fetch_crude_imports(length=5000):
    return fetch_eia(
        "crude-oil-imports/data/",
        {
            "frequency":"monthly",
            "data[0]":"quantity",
            "sort[0][column]":"period",
            "sort[0][direction]":"desc",
            "offset":0,
            "length":length
        }
    )

def fetch_wti(length=5000):
    return fetch_eia(
        "petroleum/pri/spt/data/",
        {
            "frequency":"monthly",
            "data[0]":"value",
            "facets[series][]":"RWTC",
            "sort[0][column]":"period",
            "sort[0][direction]":"desc",
            "offset":0,
            "length":length
        }
    )
