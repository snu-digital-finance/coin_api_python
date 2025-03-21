from __future__ import annotations

import json
import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pandas as pd


def find_concat_candidates(directory: str, doSort: bool = True) -> tuple:
    file_list = [
        tuple(
            s.replace('.csv', '').split('_'),
        )
        for s in sorted(os.listdir(directory))
    ]
    if len(file_list) < 2:
        return tuple()

    if doSort:
        for i in range(len(file_list) - 1):
            if file_list[i][1] == file_list[i + 1][0]:
                return (file_list[i], file_list[i + 1], directory)
    else:
        for i in range(len(file_list) - 1):
            for j in range(i + 1, len(file_list)):
                if file_list[i][1] > file_list[j][0]:
                    break
                if (
                    file_list[i][0] < file_list[j][1]
                    and file_list[i][1] == file_list[j][0]
                ):
                    return (file_list[i], file_list[j], directory)
    return tuple()


def concat_csv(a: str, b: str, directory: str) -> None:

    df = (
        pd.concat(
            [
                pd.read_csv(f"{directory}/{a[0]}_{a[1]}.csv"),
                pd.read_csv(f"{directory}/{b[0]}_{b[1]}.csv"),
            ],
        )
        .drop_duplicates()
        .sort_values('time_period_start')
    )

    os.remove(f"{directory}/{a[0]}_{a[1]}.csv")
    os.remove(f"{directory}/{b[0]}_{b[1]}.csv")
    df.to_csv(f"{directory}/{a[0]}_{b[1]}.csv", index=False)


def create_folders(periods: list[str], symbols: dict) -> None:
    for period in periods:
        os.makedirs(f"data/{period}", exist_ok=True)
        for exchange, symbol_id in symbols.items():
            if not symbol_id:
                continue
            os.makedirs(f"data/{period}/{exchange}", exist_ok=True)
            for s in (s for s in symbol_id if s):
                os.makedirs(
                    f'data/{period}/{exchange}/{"_".join(s.split("_")[1:])}',
                    exist_ok=True,
                )


def kst_to_utc(iso_time_str: str) -> str:
    kst_time = datetime.fromisoformat(iso_time_str).astimezone(
        timezone(timedelta(hours=9)),
    )
    utc_time = kst_time.astimezone(timezone.utc)
    return utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:26] + '0Z'


def look_symbols_in_exchange(exchange: str) -> None:
    with open('symbols.json') as f:
        d = json.loads(f.read())
    print({dd['symbol_id'] for dd in d if dd['exchange_id'] == exchange})


def _prepare_data(fname: str) -> pd.DataFrame:
    df = pd.read_csv(fname)
    _, period, exc, symbol, duration = fname.split('/')
    df['period'] = period
    df['exchange'] = exc
    df['symbol'] = symbol
    df['duration'] = duration.split('.')[0]
    return df.drop_duplicates()


def aggregate_data(
    output_fname: str,
    periods: list[str],
    exchanges: list[str],
    durations: list[str],
    fnames: list[str] = [],
) -> pd.DataFrame:

    fnames = fnames or sum(
        [
            [
                f"data/{period}/{exc}/{symbol}/{duration_fname}.csv"
                for symbol in os.listdir(f"data/{period}/{exc}")
                if os.path.exists(
                    f"data/{period}/{exc}/{symbol}/{duration_fname}.csv",
                )
            ]
            for period in periods
            for exc in exchanges
            for duration_fname in durations
            if os.path.exists(f"data/{period}/{exc}")
        ],
        [],
    )
    if output_fname:
        return pd.concat([_prepare_data(f) for f in fnames]).to_csv(
            output_fname, index=False,
        )

    return pd.concat([_prepare_data(f) for f in fnames])


def remove_file_by_duration(
    duration_fname: str,
    periods: list[str],
    exchanges: list[str],
) -> None:
    for x in (
        x
        for x in (
            f"data/{period}/{exc}/{symbol}"
            for period in periods
            for exc in exchanges
            for symbol in os.listdir(f"data/{period}/{exc}")
            if os.path.exists(f"data/{period}/{exc}/{symbol}")
        )
        if os.path.exists(x)
    ):
        x += f"/{duration_fname}.csv"
        if os.path.exists(x):
            os.remove(x)
