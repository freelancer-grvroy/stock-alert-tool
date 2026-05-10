import yfinance as yf
import gspread
import os
import json
import argparse
from google.oauth2.service_account import Credentials

def log_prices(mode):
    creds_info = json.loads(os.environ["GSPREAD_JSON"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("StockWatch").sheet1
    records = sheet.get_all_records()

    for i, row in enumerate(records):
        ticker = str(row.get("Ticker", "")).strip()
        if not ticker:
            continue
        try:
            stock = yf.Ticker(ticker)
            if mode == "open":
                price = round(float(stock.fast_info["open"]), 2)
                sheet.update_cell(i + 2, 6, price)
                print(f"{ticker}: Open = {price}")
            else:
                price = round(float(stock.fast_info["lastPrice"]), 2)
                sheet.update_cell(i + 2, 7, price)
                print(f"{ticker}: Close = {price}")
        except Exception as e:
            print(f"Error for {ticker}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["open", "close"], required=True)
    args = parser.parse_args()
    log_prices(args.mode)
