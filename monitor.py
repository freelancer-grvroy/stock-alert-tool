import requests
import gspread
import os
import json
from google.oauth2.service_account import Credentials

# Your provided credentials
TELEGRAM_TOKEN = "8574302533:AAHo3OVP0KoR-D_lO-DUs1OF4wcE55p0KbY"
CHAT_ID = "8412761534"

def monitor_market():
    # 1. Authenticate with Google Sheets
    creds_info = json.loads(os.environ.get("GSPREAD_JSON"))
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    
    sheet = client.open("StockWatch").sheet1
    records = sheet.get_all_records()

    for i, row in enumerate(records):
        if row!= 'Active': continue
        
        # 2. Fetch Live Price
        ticker = row
        api_url = f"https://military-jobye-haiqstudios-14f59639.koyeb.app/stock"
        params = {"symbol": ticker, "res": "num"}
        response = requests.get(api_url, params=params).json()
        ltp = response['results']['last_price']
        
        # 3. Price Comparison Logic [11]
        target = float(row)
        if ltp >= target and not row['Last Alert']:
            send_alert(f"🚀 Alert: {ticker} hit {ltp} (Target: {target})")
            # Mark as SENT in column 5 (E) to avoid duplicates
            sheet.update_cell(i + 2, 5, "SENT")

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})
