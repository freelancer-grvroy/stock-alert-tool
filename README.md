# stock-alert-tool

A collection of Python scripts that run on GitHub Actions to monitor Indian stock market (NSE/BSE) tickers tracked in a Google Sheet called **StockWatch**.

---

## Google Sheet Structure

The **StockWatch** sheet (Sheet1) is expected to have the following columns:

| Col | Header | Description |
|-----|--------|-------------|
| A | Ticker | NSE/BSE ticker symbol (e.g. `RELIANCE.NS`) |
| B | Target | Price target for alerts |
| C | ... | Other fields |
| D | Status | `Active` to enable monitoring |
| E | Last Alert | Filled with `SENT` after an alert fires |
| F | Open | Daily opening price (written by `price_logger.py`) |
| G | Close | Daily closing price (written by `price_logger.py`) |

---

## Scripts

### 1. `monitor.py` — Stock Price Alert Monitor

Checks live prices for all `Active` tickers in the StockWatch sheet and sends a **Telegram alert** when the current price hits or drops below the target.

**How it works:**
- Authenticates with Google Sheets using the `GSPREAD_JSON` secret
- Iterates rows where `Status` = `Active`
- Fetches the live last-traded price via `yfinance`
- If `current price ≤ target` and no prior alert exists, sends a Telegram message and marks the row as `SENT` in column E

**GitHub Actions workflow:** `.github/workflows/monitor.yml`
- Runs every 5 minutes on weekdays, 3:45 AM – 10:00 AM UTC (9:15 AM – 3:30 PM IST)
- Can also be triggered manually via `workflow_dispatch`

**Secrets required:**
- `GSPREAD_JSON` — Google service account credentials JSON

---

### 2. `price_logger.py` — Daily Open/Close Price Logger

Logs the daily **opening price** (column F) and **closing price** (column G) for every ticker in the StockWatch sheet. Overwrites the values each trading day.

**How it works:**
- Accepts `--mode open` or `--mode close` via CLI argument
- Authenticates with Google Sheets using the `GSPREAD_JSON` secret
- Iterates all rows with a non-empty `Ticker` value
- `--mode open`: fetches `fast_info['open']` and writes to column F
- `--mode close`: fetches `fast_info['lastPrice']` and writes to column G
- Skips empty ticker rows; logs errors per-ticker without crashing the full run

**GitHub Actions workflow:** `.github/workflows/price_logger.yml`
- Runs on weekdays at:
  - `45 3 * * 1-5` UTC → 9:15 AM IST (market open)
  - `0 10 * * 1-5` UTC → 3:30 PM IST (market close)
- Mode is auto-detected by UTC hour: `HOUR < 6` → `open`, else → `close`
- Supports `workflow_dispatch` with a manual `mode` input (`open` or `close`) for testing

**Secrets required:**
- `GSPREAD_JSON` — same Google service account credentials (no new secrets needed)

---

## Setup

1. Create a Google service account and share the **StockWatch** Google Sheet with it (Editor access)
2. Download the service account JSON key
3. Add it as a GitHub secret named `GSPREAD_JSON`
4. Push this repo — workflows will activate automatically on schedule
