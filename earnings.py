import datetime
import os
import pprint
from dotenv import load_dotenv
import finnhub
import pandas as pd
from dataCollection import dataCollection

def next_friday_date():
    today = datetime.date.today()
    days_until_friday = (4 - today.weekday() + 7) % 7
    if days_until_friday == 0:
        days_until_friday = 7  # skip this Friday
    next_friday = today + datetime.timedelta(days=days_until_friday+7)
    return next_friday.strftime("%Y-%m-%d")

def get_earnings_options_data(client):
    print("Entered")
    load_dotenv()  # Loads variables from .env into environment

    api_key = os.getenv("API_KEY")
    finnhub_client = finnhub.Client(api_key=api_key)


    # Get today's date
    today = datetime.datetime.today()   
    tmrw = today + datetime.timedelta(days=1) 
    next_friday = next_friday_date()
    print(next_friday)

    # Format as YYYY-MM-DD
    _from = today.strftime('%Y-%m-%d')
    _to = tmrw.strftime('%Y-%m-%d')  # same day if you want just one day of earnings

    response = finnhub_client.earnings_calendar(
        _from=_from,
        to=_to,
        symbol="",  # Leave empty for all symbols
        international=False
    )

    # The response is already a dict
    # You can directly parse or print it
    calendar = response.get("earningsCalendar", [])
    tickers = []
    for entry in calendar:
        tickers.append(entry["symbol"])
    stock_map = pd.Series({t: pd.DataFrame(columns=['straddlePrice', 'volatility', 'impliedMove', 'volume']) for t in tickers}) 
    for entry in calendar:
        try:
            symbol = entry["symbol"]

            response = client.option_chains(symbol=symbol, strikeCount=1, fromDate=next_friday, toDate=next_friday).json()
            if response["numberOfContracts"] == 0: continue

            straddle_price = 0.0
            volume = 0

            for exp_map_key in ("callExpDateMap", "putExpDateMap"):
                exp_map = response.get(exp_map_key, {})
                for expiry_bucket in exp_map.values():
                    for strike_level in expiry_bucket.values():
                        for contract in strike_level:
                            volatility = contract["volatility"]
                            straddle_price += contract["mark"]
                            volume += contract["totalVolume"]
                            pprint.pprint(contract)

            response = client.quote(symbol_id=symbol).json()
            asset_price = response[symbol]['quote']['mark']
            implied_move = (straddle_price / asset_price) * 100


            stock_map[symbol].loc[len(stock_map[symbol])] = {
                'straddlePrice': straddle_price,
                'volatility': volatility,
                'impliedMove': implied_move,
                'volume': volume
            }
            # Output
        except Exception as e:
            print(e)
    stock_map = stock_map[stock_map.apply(len) > 0]

    dataCollection(client, stock_map, next_friday, today)
