# 📈 SandBox Portfolio Management Workshop

A Streamlit web app for the NextGen Portfolio Management Workshop game.

## What it does
- Participants invest a simulated **$5,000,000** over a 10-year period
- Uses real historical data starting June 2016
- Includes a **COVID crash event** at month 46
- Live leaderboard comparing all participants
- CIO admin view to monitor all portfolios

## Screens
1. **Login** — Enter your name to join
2. **Asset Allocation** — Set portfolio weights (must total 100%)
3. **Dashboard** — Live portfolio performance & leaderboard

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How to Deploy (Free) on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Select `app.py` as the main file
5. Click Deploy — get a shareable link instantly!

## Asset Classes
- US Equities
- European Equities
- Emerging Markets
- Global Bonds
- Real Estate (REIT)
- Gold
- Cash

## Workshop Flow
| Time | Event |
|------|-------|
| Session 1 (Day 1, 8AM) | Participants set initial allocation |
| Month 46 (~11:30 PM Day 1) | COVID crash — rebalance window |
| Session 2 (Day 2, 9AM) | Final rebalance opportunity |
| Final Session (Day 2, 4PM) | Results revealed, winner announced |
