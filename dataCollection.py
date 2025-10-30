import datetime
import keyboard  # pip install keyboard'
import time


def dataCollection(client, stock_map, next_friday, today):
    today = datetime.datetime.today()   
    tmrw = today + datetime.timedelta(days=1) 

    # Format as YYYY-MM-DD
    _from = today.strftime('%Y-%m-%d')
    _to = tmrw.strftime('%Y-%m-%d')
    while not keyboard.is_pressed('q'):
        for key, dataframe in stock_map.items():
            try:
                response = client.option_chains(symbol=key, strikeCount=1, fromDate=next_friday, toDate=next_friday).json()

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

                response = client.quote(symbol_id=key).json()
                asset_price = response[key]['quote']['mark']
                implied_move = (straddle_price / asset_price) * 100


                dataframe.loc[len(stock_map[key])] = {
                    'timestamp': time.time()*1000,
                    'straddlePrice': straddle_price,
                    'assetPrice': asset_price,
                    'volatility': volatility,
                    'impliedMove': implied_move,
                    'volume': volume
                }
            except Exception as e:
                print(e)

        now = datetime.datetime.now()
        next_minute = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        sleep_seconds = (next_minute - datetime.datetime.now()).total_seconds()

        while sleep_seconds > 0:
            if keyboard.is_pressed('q'):
                print("Stopping loop!")
                break
            time.sleep(min(0.1, sleep_seconds))  # sleep max 0.1s at a time
            sleep_seconds -= 0.1
    for symbol, df in stock_map.items():
        if not df.empty:  # skip empty DataFrames
            df.to_csv(f"{symbol}.csv", index=False)
