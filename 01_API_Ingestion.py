# Databricks notebook source
import requests
import time
from pyspark.sql.functions import *
from datetime import datetime, timedelta

print("="*60)
print("CURRENCY EXCHANGE DATA INGESTION")
print("="*60)

BASE_URL = "https://api.frankfurter.app"

def safe_get(url, params=None, retries=3):
    for attempt in range(retries):
        try:
            start = time.time()
            resp = requests.get(url, params=params, timeout=10)
            latency = time.time() - start
            print(f"Request latency: {latency:.2f} sec")

            if resp.status_code == 200:
                return resp
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(2)
    raise Exception("❌ API request failed after retries.")

print("Fetching latest exchange rates...")
response = safe_get(f"{BASE_URL}/latest")

data = response.json()
print(f"✅ Retrieved {len(data['rates'])} currencies")

records = [
    {
        'date': data['date'],
        'base_currency': data['base'],
        'target_currency': c,
        'exchange_rate': float(r),
        'fetch_timestamp': datetime.now()
    }
    for c, r in data['rates'].items()
]

df_latest = spark.createDataFrame(records)
df_latest.write.format("delta").mode("overwrite").saveAsTable("currency_project.raw_data.latest_rates")

print(f"✅ Saved {df_latest.count()} latest exchange rates")
display(df_latest.limit(5))

# Historical ingestion
print("\nFetching historical data...")
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

historical_url = f"{BASE_URL}/{start_date}..{end_date}"
params = {'from': 'EUR', 'to': 'USD,GBP,JPY,CAD,AUD,CHF'}

response = safe_get(historical_url, params=params)
historical_data = response.json()

records = []
for date_str, rates in historical_data['rates'].items():
    for cur, rate in rates.items():
        records.append({
            'date': date_str,
            'base_currency': 'EUR',
            'target_currency': cur,
            'exchange_rate': float(rate),
            'fetch_timestamp': datetime.now()
        })

df_historical = spark.createDataFrame(records)
df_historical.write.format("delta").mode("overwrite").saveAsTable("currency_project.raw_data.historical_rates")

print(f"✅ Saved {df_historical.count()} historical records")
