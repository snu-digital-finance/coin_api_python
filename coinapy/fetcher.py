from __future__ import annotations

import json
import os

import pandas as pd

from .api import base_caller

EXCHANGES = ['UPBIT', 'BITHUMB']  # 업비트 & 빗썸 거래소 심볼 조회
PERIODS = ['5SEC', '1MIN']  # 5초, 1분 단위 데이터
ASSET_TYPES = {
    'spot': '_SPOT_',
    'future': '_FTX_',
    'option': '_OPT_',
    'swap': '_SWAP_',
    'index': '_IND_',
    'perp': '_PERP_',
}


def _get_all_symbols():
    if os.path.exists('symbols.json'):
        with open('symbols.json') as f:
            return json.loads(f.read())
    data = base_caller('symbols')
    with open('symbols.json', 'w') as f:
        f.write(json.dumps(data))
    return data


def get_exchange_symbols(
    target: str = 'BTC',
    exchanges: list[str] = ['UPBIT', 'BITHUMB'],
    types: list[str] = ['spot'],
    currency: list[str] = ['KRW', 'USDT', 'USDC', 'USD'],
) -> dict:
    data = _get_all_symbols()
    if not data:
        return {}

    symbols: dict[str, list] = {}
    for item in data:
        exchange_id = item.get('exchange_id')
        asset_id_base = item.get('asset_id_base')
        asset_id_quote = item.get('asset_id_quote')
        symbol_id = item.get('symbol_id')
        for t in types:
            if ASSET_TYPES[t.lower()] not in symbol_id:
                continue

            if (
                asset_id_base == target
                and asset_id_quote in currency
                and exchange_id in exchanges
            ):
                if exchange_id not in symbols:
                    symbols[exchange_id] = []
                symbols[exchange_id].append(symbol_id)

    return symbols


def get_ohlcv(
    symbol_id: str,
    period: str,
    time_start: str,
    time_end: str,
    limit: int = 1000,
) -> pd.DataFrame:
    data = base_caller(
        path=f"ohlcv/{symbol_id}/history",
        params={
            'period_id': period,
            'time_start': time_start,
            'time_end': time_end,
            'limit': limit,
        },
    )
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    print(f"✅ {symbol_id} - {period} downloaded! ({len(df)} rows)")
    return df
