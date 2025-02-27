import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEYS = [os.getenv('COINAPI_KEY1'), os.getenv('COINAPI_KEY2'), os.getenv('COINAPI_KEY3')]

# API 호출 함수
def call_api(endpoint, params=None, retries=3, wait_time=5):
    params = params or {}

    for api_key in API_KEYS:
        params["api_key"] = api_key  # 현재 API 키 추가
        
        for attempt in range(retries):
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json()  # 성공 시 JSON 반환
            elif response.status_code == 429:  # Rate limit 초과
                print(f"Rate limit exceeded for {api_key}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)  # 대기 후 재시도
                break  # 같은 API 키로 재시도
            else:
                print(f"Error {response.status_code}: {response.text}")
                break  # 다른 오류 발생 시 즉시 중단
    
    raise Exception("All API keys exhausted or request failed")

# 사용 예시
if __name__ == "__main__":
    endpoint = "https://api.example.com/data"
    params = {"query": "example"}
    
    try:
        result = call_api(endpoint, params)
        print(result)
    except Exception as e:
        print(f"API call failed: {e}")