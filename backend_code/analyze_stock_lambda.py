# analyze_stock_lambda.py (AWS Lambda handler)
import json
from stock_analysis import (
    fetch_balance_sheet,
    fetch_news_headlines,
    fetch_historical_price,
    fetch_current_price,
    build_prompt
)
from llama_inference import call_llama3

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters", {})
        ticker = params.get("ticker", "").upper()
        quantity = params.get("quantity")
        buy_date = params.get("buy_date")

        if not ticker:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Ticker is required"})
            }

        financials = fetch_balance_sheet(ticker)
        news = fetch_news_headlines(ticker)

        if not financials or not news:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Data fetch failed"})
            }

        # If new investor (no quantity or date)
        if not quantity or not buy_date:
            prompt = f"""
You are an AI financial assistant. Based on the following:

Financials:
- Cash: ${financials['cash']}
- Debt: ${financials['debt']}
- Retained Earnings: ${financials['retained']}

Recent News:
{chr(10).join(f"- {item['title']} ({item['source']})" for item in news)}

Return:
Decision: BUY / DON'T BUY
Reason: 1-2 lines
Decision made using news:
{chr(10).join(f"- {item['title']} ({item['source']})" for item in news)}
"""
            result = call_llama3(prompt)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "ticker": ticker,
                    "decision_result": result.strip(),
                    "news": news,
                    "financials": financials
                })
            }

        # If user already owns the stock
        buy_price = fetch_historical_price(ticker, buy_date)
        current_price = fetch_current_price(ticker)

        if not buy_price or not current_price:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Price data not available"})
            }

        prompt = build_prompt(ticker, news, financials, int(quantity), buy_price, current_price)
        result = call_llama3(prompt)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "ticker": ticker,
                "decision_result": result.strip(),
                "news": news,
                "financials": financials,
                "buy_price": buy_price,
                "current_price": current_price
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
