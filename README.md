# 📈  Financial Dashboard – Streamlit serenade to the markets  
_A lyrical voyage through price, volume & value_

> “The market’s pulse is poetry in numbers.”  

Welcome to **Financial Dashboard v3**, a Streamlit application that turns raw market data into symphonies of charts, stats and Monte-Carlo dreams. Point it at any S&P 500 ticker and watch it sing.

---

## ✨  Features

| Tab | What it does | Why you’ll care |
|-----|--------------|-----------------|
| **Company profile** | Business summary + key stats pulled live from Yahoo Finance. | Skip the 10-K; keep the gist. |
| **Chart** | Line or candlestick price plots, 50-day moving average & color-coded volume. | Spot trends faster than you can say “bull flag.” |
| **Summary** | Profile, stats table, interactive candlestick & shareholder breakdown. | One-pager for your investment thesis. |
| **Monte Carlo Simulation** | Up to 2 000 simulated price paths & VaR ₉₅. | Peek into tomorrow’s fog (with probabilistic humility). |
| **Financials** | Income statement, balance sheet or cash-flow—annual or quarterly. | Because fundamentals still matter—sometimes. |
| **News** | Latest articles + timestamps & publishers. | Stay current without tab-surfing. |

---

## 🚀  Quick start

```bash
# 1. Clone the repo
git clone https://github.com/<your-user>/financial-dashboard.git
cd financial-dashboard

# 2. Create & activate a virtual environment (optional but tidy)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run finapp.py
