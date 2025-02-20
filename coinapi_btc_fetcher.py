import requests
import pandas as pd
import os
import time
from itertools import cycle
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
API_KEYS = [os.getenv('COINAPI_KEY1'), os.getenv('COINAPI_KEY2'), os.getenv('COINAPI_KEY3')]
API_KEYS = [key for key in API_KEYS if key]  # 빈 값 제거
api_key_cycle = cycle(API_KEYS)  # API 키 순환

BASE_URL = "https://rest.coinapi.io/v1"
EXCHANGES = ["UPBIT", "BITHUMB"]  # 업비트 & 빗썸 거래소 심볼 조회
PERIODS = ["5SEC", "1MIN"]  # 5초, 1분 단위 데이터

def get_exchange_symbols():
    api_key = next(api_key_cycle)
    headers = {"Accept": "application/json", "X-CoinAPI-Key": api_key}
    url = f"{BASE_URL}/symbols"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        symbols = {ex: None for ex in EXCHANGES}
        for item in data:
            exchange_id = item.get("exchange_id")
            asset_id_base = item.get("asset_id_base")
            asset_id_quote = item.get("asset_id_quote")
            symbol_id = item.get("symbol_id")

            if exchange_id in EXCHANGES and asset_id_base == "BTC" and asset_id_quote in ["KRW", "USDT"]:
                symbols[exchange_id] = symbol_id  # 데이터 수집을 위해 BTC/KRW 또는 BTC/USDT 

        return symbols
    else:
        print(f"❌ 거래소 심볼 조회 실패: {response.status_code}, {response.text}")
        return None

def fetch_data(symbol_id, period):
    """
    원하는 주기에 따라서 OHLCV 데이터를 가져온다. (5SEC, 1MIN)
    """
    url = f"{BASE_URL}/ohlcv/{symbol_id}/latest"
    api_key = next(api_key_cycle)
    headers = {"Accept": "application/json", "X-CoinAPI-Key": api_key}
    params = {"period_id": period, "limit": 1000}

    for attempt in range(3): # range 수정 가능.. 오류 헨들링.
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            print(f"✅ {symbol_id} - {period} 데이터 수집 성공! ({len(df)} rows)")
            print(df.head())  # 상위 5개만 출력 # 데이터 불러오는 시간이 생각보다 기네요.
            return df
        elif response.status_code == 429:
            print(f"⏳ API 호출 제한! 10초 후 재시도 ({attempt + 1}/3)")
            time.sleep(10) 
        else:
            print(f"❌ 요청 실패:  {response.status_code}, {response.text}")
            break
    return None

# 거래소 심볼 조회
symbols = get_exchange_symbols()
if symbols:
    for exchange, symbol_id in symbols.items():
        if symbol_id:
            print(f"📌 {exchange} BTC symbol_id: {symbol_id}")
            for period in PERIODS:
                fetch_data(symbol_id, period)
        else:
            print(f"⚠ {exchange}에서 BTC 심볼을 찾을 수 없습니다.")