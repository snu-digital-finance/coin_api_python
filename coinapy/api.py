from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv
import requests
import os
import yaml
import time
from itertools import cycle

@dataclass
class Config:
    IS_PAID: bool
    top_25_exchanges: List[str]
    HEADERS: Dict = field(default_factory=dict)
    BASE_URL: str = field(default="https://rest.coinapi.io/v1")
    



with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

config = Config(**config)
config.HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "deflate, gzip"
}

load_dotenv()
print(config.IS_PAID)
if config.IS_PAID:
    api_key_cycle = cycle([os.getenv("COINAPI_PAID_KEY")])
else:
    api_key_cycle = cycle([
        value for key, value in os.environ.items() if 'COINAPI_KEY' in key
    ])




def base_caller(path:str, params:dict={}, retries:int=3) -> dict:
    
    for attempt in range(retries):
        config.HEADERS["X-CoinAPI-Key"] = params["apikey"] = next(api_key_cycle)
        response = requests.get(
            os.path.join(config.BASE_URL, path),
            headers=config.HEADERS,
            params=params
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"⏳ Limit for requesting! Retry after 10 sec ({attempt + 1}/3)")
            time.sleep(10)
        else:       
            print(f"❌ Failed:  {response.status_code}, {response.text}")
            raise requests.exceptions.ConnectionError
    
    print("Retry Over")
    return {}
    