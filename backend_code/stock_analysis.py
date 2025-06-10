
import requests
from datetime import datetime


FMP_API_KEY = "fGHM7fruyYs5vcUwJWTzjwgzwekHcqWB"


from datetime import datetime,timedelta

def fetch_historical_price(ticker, date):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={FMP_API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        print("FMP price error:", res.text)
        return None

    data = res.json()
    historical = data.get("historical", [])

    # Convert the date string to datetime
    target_date = datetime.strptime(date, "%Y-%m-%d")

    # Find the closest available trading date
    closest = None
    min_diff = float("inf")

    for item in historical:
        item_date = datetime.strptime(item["date"], "%Y-%m-%d")
        diff = abs((item_date - target_date).days)
        if diff < min_diff:
            min_diff = diff
            closest = item

    if not closest:
        print("No historical price found close to:", date)
        return None

    return round(closest.get("close", 0), 2)


def fetch_current_price(ticker):
    url = f"https://financialmodelingprep.com/api/v3/quote-short/{ticker}?apikey={FMP_API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        return None

    data = res.json()
    if not data:
        return None

    return round(data[0].get("price", 0), 2)
def fetch_balance_sheet(ticker):
    url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit=1&apikey={FMP_API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        print("FMP error:", res.text)
        return None

    data = res.json()
    if not data or not isinstance(data, list):
        return None

    bs = data[0]  # Get the latest record
    return {
        "cash": bs.get("cashAndCashEquivalents", 0),
        "debt": bs.get("totalDebt", 0),
        "retained": bs.get("retainedEarnings", 0)
    }
seven_days= (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
def fetch_news_headlines(ticker):
    from datetime import datetime, timedelta
    seven_days_ago = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = f"{ticker} stock"
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&from={seven_days_ago}&sortBy=publishedAt&pageSize=5&apiKey=ebc21a63a9154bae84ecb8a97b0608a5"
    )
    res = requests.get(url)

    if res.status_code != 200:
        print("NewsAPI error:", res.text)
        return []

    articles = res.json().get("articles", [])[:3]
    return [{"title": a["title"], "source": a["source"]["name"]} for a in articles]

def build_prompt(ticker, news, financials, quantity, buy_price, current_price):
    # gain = ((current_price - buy_price) / buy_price) * 100
    news_lines = "\n".join(f"- {item['title']} ({item['source']})" for item in news)

    few_shot_examples = """
<Example 1>
<prompt>
User owns 20 shares of MSFT, bought at $280. Current price is $300.
Financials:
- Cash: $104B
- Debt: $60B
- Retained Earnings: $200B
News:
- Microsoft reports strong cloud growth (CNBC)
- AI Copilot announced for Office 365 (The Verge)

<your output>
Decision: BUY MORE
Reason: Strong financials and bullish news indicate continued upside.
Decision made using news:
- Microsoft reports strong cloud growth (CNBC)
- AI Copilot announced for Office 365 (The Verge)

Project By: MANAV

<Example 2>
<prompt>
User owns 50 shares of TSLA, bought at $260. Current price is $240.
Financials:
- Cash: $22B
- Debt: $15B
- Retained Earnings: $10B
News:
- Tesla faces production slowdown in Shanghai (Bloomberg)
- Analysts downgrade TSLA amid competition (Reuters)

<Your output>
Decision: SELL HALF
Reason: Moderate loss and negative outlook justify reducing position.
Decision made using news:
- Tesla faces production slowdown in Shanghai (Bloomberg)
- Analysts downgrade TSLA amid competition (Reuters)

Project By: MANAV
"""

    actual_case = f"""
<User Case> you are investment advisor. And on basis of below details give output as defined in examples exactly.Do not give code never.
User owns {quantity} shares of {ticker}, bought at ${buy_price:.2f}. Current price is ${current_price:.2f}.
Financials:
- Cash: ${financials['cash']}
- Debt: ${financials['debt']}
- Retained Earnings: ${financials['retained']}
News:
{news}

<your output>
"""

    return few_shot_examples + "\n" + actual_case
