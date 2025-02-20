import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time

load_dotenv()
API_KEY = os.getenv('COINAPI_KEY1') # 단일

def call_api(endpoint, params=None, retries=3):
    params = params or {}
    params["apikey"] = API_KEY
    
    for attempt in range(retries):
        response = requests.get(endpoint, params=params)
        
        #  오류 핸들링
        if response.status_code == 200:
            return response.json() 
        elif response.status_code == 429:  
            print(f"Rate limit exceeded for {API_KEY}. Retrying...")
            time.sleep(5)  # 대기 후 재시도
            break
        else:
            print(f"Error {response.status_code}: {response.text}")
            break
    
    raise Exception("Request failed")

# 데이터 수집 함수
# 여기서 endpoint를 수정해도 안 됨.
def fetch_historical_data(symbol_id, time_start, time_end, interval='1m'):
    endpoint = f"https://rest.coinapi.io/v1/orderbooks/:symbol_id/history"  # 올바른 endpoint 설정(?)
    params = {
        'period_id': interval,
        'time_start': time_start,
        'time_end': time_end,
        'limit': 1
    }
    
    try:
        result = call_api(endpoint, params)
        return result  # 결과 반환
    except Exception as e:
        print(f"Error fetching data for {symbol_id}: {e}")
        return None

def check_data_availability(symbol_id, time_start, time_end):
    intervals = ['1m', '30s']
    results = {}

    for interval in intervals:
        data = fetch_historical_data(symbol_id, time_start, time_end, interval)
        results[interval] = data is not None and len(data) > 0  # 데이터가 존재하면 True, 아니면 False

    return results


if __name__ == "__main__":
    combinations = [
        "UPBIT:BTC_KRW",
        "BITHUMB:ETH_KRW"
    ]

    time_start = "2024-12-03T22:23:00"
    time_end = "2024-12-03T22:24:00"

    availability_results = {}

    for symbol in combinations:
        availability_results[symbol] = check_data_availability(symbol, time_start, time_end)

    # 결과 출력
    for symbol, availability in availability_results.items():
        print(f"Data availability for {symbol}: {availability}")