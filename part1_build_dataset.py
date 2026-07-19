"""Team 1: download 10,000 hourly Binance kline records.
Run: python part1_build_dataset.py
"""
from __future__ import annotations
import csv, json, threading, time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

# Using Cryptocurrency tags provided in CW Brief

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT","LINKUSDT","DOTUSDT"]

# Setting parameters to process request issued to attain Binance Data

INTERVAL="1h"; LIMIT=1000; MAX_WORKERS=5; MAX_REQUESTS_PER_MINUTE=100

# This URL is linked to Public Library of Binance. 

BASE_URL="https://data-api.binance.vision/api/v3/klines"

# Saving clean data

DATA_FILE=Path("data/clean/clean_market_data.csv")

# This records when each API request starts, finishes or fails.

LOG_FILE=Path("results/api_download.log")

# This records the time taken by each thread to obtain data 

RUNTIME_FILE=Path("results/runtime_comparison.csv")
FIELDS=["symbol","interval","open_time","open","high","low","close","volume","close_time","quote_volume","trade_count","taker_buy_base_volume","taker_buy_quote_volume"]

# Log Lock ensures only one request is sent to the Log file at a time so the requests do not overlap. 
log_lock=threading.Lock(); request_semaphore=threading.Semaphore(MAX_WORKERS)
rate_lock=threading.Lock(); request_times=deque()

def utc_now(): return datetime.now(timezone.utc).isoformat()
def log(message):
    line=f"{utc_now()} | {message}"
    with log_lock:
        LOG_FILE.parent.mkdir(parents=True,exist_ok=True)
        with LOG_FILE.open("a",encoding="utf-8") as f: f.write(line+"\n")
    print(line)

def wait_for_rate_limit():
    while True:
        with rate_lock:
            now=time.monotonic()
            while request_times and now-request_times[0]>=60: request_times.popleft()
            if len(request_times)<MAX_REQUESTS_PER_MINUTE:
                request_times.append(now); return
            wait=max(0.01,60-(now-request_times[0]))
        log(f"RATE_LIMIT wait_seconds={wait:.2f}"); time.sleep(wait)

def convert(symbol, record):
    def ts(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat()
    return {"symbol":symbol,"interval":INTERVAL,"open_time":ts(record[0]),"open":record[1],"high":record[2],"low":record[3],"close":record[4],"volume":record[5],"close_time":ts(record[6]),"quote_volume":record[7],"trade_count":record[8],"taker_buy_base_volume":record[9],"taker_buy_quote_volume":record[10]}

def fetch_symbol(symbol):
    params=urlencode({"symbol":symbol,"interval":INTERVAL,"limit":LIMIT})
    with request_semaphore:
        wait_for_rate_limit(); log(f"START request symbol={symbol} interval={INTERVAL} limit={LIMIT}")
        try:
            with urlopen(f"{BASE_URL}?{params}",timeout=30) as response: payload=json.load(response)
        except Exception as exc:
            log(f"ERROR symbol={symbol} error={exc}"); raise
        if not isinstance(payload,list) or len(payload)!=LIMIT: raise RuntimeError(f"Expected {LIMIT} rows for {symbol}, received {len(payload) if isinstance(payload,list) else 'invalid response'}")
        rows=[convert(symbol,r) for r in payload]; log(f"END request symbol={symbol} records={len(rows)}"); return rows

def download_serial():
    rows=[]
    for symbol in SYMBOLS: rows.extend(fetch_symbol(symbol))
    return rows

def download_threaded():
    by_symbol={}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures={pool.submit(fetch_symbol,s):s for s in SYMBOLS}
        for future in as_completed(futures): by_symbol[futures[future]]=future.result()
    return [row for symbol in SYMBOLS for row in by_symbol[symbol]]

def timed(fn):
    start=time.perf_counter(); rows=fn(); return rows,time.perf_counter()-start

def write_csv(rows):
    DATA_FILE.parent.mkdir(parents=True,exist_ok=True)
    with DATA_FILE.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    log(f"WROTE csv={DATA_FILE} records={len(rows)}")

def main():
    DATA_FILE.parent.mkdir(parents=True,exist_ok=True); LOG_FILE.parent.mkdir(parents=True,exist_ok=True); LOG_FILE.write_text("",encoding="utf-8")
    print(f"Symbols configured: {len(SYMBOLS)}\nInterval: {INTERVAL}\nLimit per symbol: {LIMIT}\nExpected records: {len(SYMBOLS)*LIMIT}")
    serial_rows,serial_seconds=timed(download_serial)
    request_times.clear()
    threaded_rows,threaded_seconds=timed(download_threaded)
    if len(threaded_rows)!=10000: raise RuntimeError(f"Record count check failed: {len(threaded_rows)}")
    write_csv(threaded_rows)
    with RUNTIME_FILE.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["method","seconds","records","note"]); w.writeheader(); w.writerow({"method":"serial","seconds":f"{serial_seconds:.4f}","records":len(serial_rows),"note":"downloaded the ten symbols one after another"}); w.writerow({"method":"multithreading","seconds":f"{threaded_seconds:.4f}","records":len(threaded_rows),"note":"downloaded several symbols at the same time"})
    print(f"Saved: {DATA_FILE}\nTotal records saved: {len(threaded_rows)}\nRecord count check: passed\nSaved: {RUNTIME_FILE}\nScript completed successfully")
if __name__=="__main__": main()
