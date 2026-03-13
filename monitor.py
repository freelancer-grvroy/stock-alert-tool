import requests
import gspread
import os
import json
from google.oauth2.service_account import Credentials

# Configuration
TELEGRAM_TOKEN = "8574302533:AAHo3OVP0KoR-D_lO-DUs1OF4wcE55p0KbY"
CHAT_ID = "8412761534"

def monitor_market():
    try:
        # 1. Authenticate
        print("--- Authenticating with Google Sheets ---")
        creds_info = json.loads(os.environ.get("GSPREAD_JSON"))
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # 2. Open Sheet
        sheet = client.open("StockWatch").sheet1
        records = sheet.get_all_records()
        print(f"Total stocks found in sheet: {len(records)}")

        for i, row in enumerate(records):
            # Print row for debugging (keys are case-sensitive)
            print(f"Processing Row {i+1}: {row}")
            
            # Check Status
            if str(row.get('Status')).strip()!= 'Active':
                print(f"Skipping {row.get('Ticker')}: Status is {row.get('Status')} (Expected 'Active')")
                continue
            
            ticker = row.get('Ticker')
            target = float(row.get('Target', 0))
            last_alert = row.get('Last Alert')
            
            # 3. Fetch Price
            api_url = f"https://military-jobye-haiqstudios-14f59639.koyeb.app/stock"
            params = {"symbol": ticker, "res": "num"}
            response = requests.get(api_url, params=params).json()
            ltp = response['results']['last_price']
            print(f"Checked {ticker}: Current Price={ltp}, Target={target}")
            
            # 4. Logical Check
            if ltp >= target and not last_alert:
                print(f"🎯 Target hit for {ticker}! Sending Telegram alert...")
                send_alert(f"🚀 Alert: {ticker} hit {ltp} (Target: {target})")
                sheet.update_cell(i + 2, 5, "SENT")
            elif last_alert:
                print(f"Skipping {ticker}: Alert already marked as SENT.")

    except Exception as e:
        print(f"❌ Error during execution: {e}")

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

if __name__ == "__main__":
    monitor_market()
