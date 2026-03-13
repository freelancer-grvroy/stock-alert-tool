import yfinance as yf
import gspread
import os
import json
import requests
from google.oauth2.service_account import Credentials

# Configuration from your provided details
TELEGRAM_TOKEN = "8574302533:AAHo3OVP0KoR-D_lO-DUs1OF4wcE55p0KbY"
CHAT_ID = "8412761534"

def monitor_market():
    try:
        # 1. Authenticate with Google Sheets
        creds_info = json.loads(os.environ.get("GSPREAD_JSON"))
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # 2. Open Sheet
        sheet = client.open("StockWatch").sheet1
        records = sheet.get_all_records()

        for i, row in enumerate(records):
            # Check if status is Active
            if str(row.get('Status')).strip()!= 'Active':
                continue
            
            ticker = row.get('Ticker')
            target = float(row.get('Target', 0))
            last_alert = row.get('Last Alert')
            
            # 3. Fetch Price using yfinance (High Reliability)
            stock = yf.Ticker(ticker)
            ltp = stock.fast_info['lastPrice']
            print(f"Checked {ticker}: Current Price={round(ltp, 2)}, Target={target}")
            
            # 4. Logical Check for alert
            if ltp >= target and not last_alert:
                print(f"🎯 Target hit for {ticker}! Sending Telegram alert...")
                msg = f"🚀 *Stock Alert: {ticker}*\nPrice: {round(ltp, 2)}\nTarget: {target}"
                send_alert(msg)
                # Mark as SENT in your Google Sheet to prevent repeat alerts [1]
                sheet.update_cell(i + 2, 5, "SENT")

    except Exception as e:
        print(f"❌ Error during execution: {e}")

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    # This will show us the REAL error in GitHub Actions logs
    print(f"Telegram Response: {response.status_code} - {response.text}")

if __name__ == "__main__":
    monitor_market()
