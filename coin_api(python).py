from dotenv import load_dotenv
import requests
import pandas as pd
import os

# 필요하신 분은 .env 파일에다가 자신의 api 키 파일 넣으시면 됩니다. 
load_dotenv()
api_key = os.getenv('COINAPI_KEY')
print(api_key)

# 상위 25개 거래소 목록
top_25_exchanges = [
    "BINANCE", "KRAKEN", "COINBASE", "BITFINEX", "BITSTAMP", "HUOBI", "BYBIT", 
    "FTX", "KUCOIN", "GEMINI", "BITHUMB", "POLONIEX", "BLOC", "COINEX", "CEXIO", 
    "KRAKEN_FUTURES", "GATEIO", "BITGET", "MEXC", "COINONE", "COINSBIT", "LATOKEN", 
    "EXMO", "ZB_COM", "BTC_MARKETS"
]

# 요청할 API의 기본 URL
# 상위 25개의 거래소 경우 coinmarcketcap의 데이터를 사용.
base_url = "https://rest.coinapi.io/v1/symbols"

# API 요청 설정
headers = {
    'Accept': 'application/json',
    'X-CoinAPI-Key': api_key
}

# 각 거래소의 법정통화 및 스테이블코인 정보를 저장할 리스트
exchange_currencies = []

# 거래소마다 데이터 요청
for exchange_id in top_25_exchanges:
    url = f"{base_url}/map/{exchange_id}"  # 거래소 ID를 URL에 포함
    response = requests.get(url, headers=headers)
    
    # 응답 상태 확인
    if response.status_code == 200:
        data = response.json()
        print(f"{exchange_id}의 데이터를 성공적으로 가져왔습니다.")
        
        # 각 거래소의 법정통화/스테이블코인 추출.
        # .cvs 파일로 추출.(액셀)
        for item in data:
            asset_id_base = item.get('asset_id_base')  # 'asset_id_base'가 없을 경우 None 반환
            asset_id_quote = item.get('asset_id_quote')  # 'asset_id_quote'가 없을 경우 None 반환
            
            if asset_id_base and asset_id_quote:
                # 법정통화 및 스테이블코인 확인 (USDT, USD, EUR 등)
                # USDC 등 
                if asset_id_base in ['USDT', 'USD', 'EUR', 'GBP', 'CNY', 'JPY', 'KRW'] or \
                   asset_id_quote in ['USDT', 'USD', 'EUR', 'GBP', 'CNY', 'JPY', 'KRW']:
                    exchange_currencies.append({
                        'exchange_id': exchange_id,
                        'asset_id_base': asset_id_base,
                        'asset_id_quote': asset_id_quote
                    })
    else:
        print(f"{exchange_id}의 데이터를 가져오는 데 실패. 상태 코드: {response.status_code}")

# 결과를 DataFrame으로 변환
df = pd.DataFrame(exchange_currencies)

# 엑셀로 저장
df.to_excel('exchange_currencies.xlsx', index=False)
print("법정통화 or 스테이블코인 정보 -> 'exchange_currencies.xlsx' 파일로 저장.")