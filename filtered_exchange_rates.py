import pandas as pd

df = pd.read_excel('exchange_currencies.xlsx')
df = df[df['exchange_id'].isin(
    ["BINANCE", 'BYBIT', 'COINBASE', 'BITGET', 'UPBIT', 'BITHUMB']
)]
df["asset_id_base"] = df["asset_id_base"].str.strip()
df = df[df["asset_id_base"].isin([
    'BTC', 'ETH', 'TRX', 'XRP'
])]

sort_order = ['USD', 'USDT', 'KRW', 'EUR', 'GBP', 'CNY', 'JPY']
df.asset_id_quote = df.asset_id_quote.astype(
    pd.CategoricalDtype(categories=sort_order, ordered=True)
)

df = df.sort_values([
    'exchange_id', 'asset_id_base', 'asset_id_quote'
]).drop_duplicates(
    subset=['exchange_id', 'asset_id_base'], keep='first'
)

# 결과를 터미널에 출력
print(df)