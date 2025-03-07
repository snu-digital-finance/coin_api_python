from __future__ import annotations

import os
import time
from dataclasses import dataclass
from dataclasses import field
from itertools import cycle

import requests
import yaml
from dotenv import load_dotenv


@dataclass
class Config:
    IS_PAID: bool
    top_25_exchanges: list[str]
    currency_order: list[str]
    HEADERS: dict = field(default_factory=dict)
    BASE_URL: str = field(default='https://rest.coinapi.io/v1')


handlers = {
    200: lambda response, _: response.json(),
    429: lambda _, attempt: (
        print(f"⏳ Limit for requesting! Retry after 10 sec ({attempt + 1}/3)"),
        time.sleep(10),
    ),
}


with open('config.yml') as f:
    config = yaml.safe_load(f)

config = Config(**config)
config.HEADERS = {
    'Accept': 'application/json',
    'Accept-Encoding': 'deflate, gzip',
}

load_dotenv()
print(config.IS_PAID)
if config.IS_PAID:
    api_key_cycle = cycle([os.getenv('COINAPI_PAID_KEY')])
else:
    api_key_cycle = cycle(
        [value for key, value in os.environ.items() if 'COINAPI_KEY' in key],
    )


def _process_response(response, attempt):
    return handlers.get(
        response.status_code,
        lambda res, _: (
            print(f"❌ Failed: {res.status_code}, {res.text}"),
            exec('raise requests.exceptions.ConnectionError'),
        ),
    )(response, attempt)


def base_caller(path: str, params: dict = {}, retries: int = 3) -> dict:
    for attempt in range(retries):
        config.HEADERS['X-CoinAPI-Key'] = params['apikey'] = next(
            api_key_cycle,
        )
        response = requests.get(
            os.path.join(config.BASE_URL, path),
            headers=config.HEADERS,
            params=params,
        )

        result = _process_response(response, attempt)
        if result == []:
            print('Empty Data')
            return {}
        if result:
            return result

    print('Retry Over')
    return {}
