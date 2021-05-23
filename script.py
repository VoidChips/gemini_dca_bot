import requests
import json
import base64
import hmac
import hashlib
import datetime
import time
import config

# convert dollar amount to coin amount
def fiatToCrypto(dollars, coin_price):
    amount = dollars / coin_price
    amount = round(amount, 6)  # round to 6 decimal places
    return amount

# get the api keys from config.py
gemini_api_key = config.gemini_api_key
gemini_api_secret = config.gemini_api_secret

base_url = "https://api.gemini.com"
endpoint = "/v1/order/new"
url = base_url + endpoint

limitBuyOrderCreated = False

while True:
    # get btc's price and convert to float
    response = requests.get(base_url + "/v1/pubticker/btcusd")
    btc_data = response.json()
    btc_price = float(btc_data['last'])

    # get eth's price and convert to float
    response = requests.get(base_url + "/v1/pubticker/ethusd")
    eth_data = response.json()
    eth_price = float(eth_data['last'])

    # get the amount of bitcoin and ethereum that will be purchased
    btc_amount = fiatToCrypto(40.0, btc_price)
    eth_amount = fiatToCrypto(40.0, eth_price)

    t = datetime.datetime.now()
    payload_nonce = str(int(time.mktime(t.timetuple())*1000))

    btc_payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": str(btc_amount),
        "price": str(btc_price - 200),  # set the price to buy at
        "side": "buy",
        "type": "exchange limit",
        "options": ["maker-or-cancel"]
    }

    encoded_payload = json.dumps(btc_payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    btc_request_headers = {'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': gemini_api_key,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache"}

    time.sleep(1)  # wait 1 second
    t = datetime.datetime.now()
    payload_nonce = str(int(time.mktime(t.timetuple())*1000))

    eth_payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "ethusd",
        "amount": eth_amount,
        "price": str(eth_price - 20),  # set the price to buy at
        "side": "buy",
        "type": "exchange limit",
        "options": ["maker-or-cancel"]
    }

    encoded_payload = json.dumps(eth_payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    eth_request_headers = {'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': gemini_api_key,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache"}

    today = datetime.datetime.today()
    weekday = today.weekday()

    # buy each coin once on sundays
    if weekday == 6 and not limitBuyOrderCreated:
        # display current price of btc and eth
        print(f"BTC: ${btc_price}")
        print(f"ETH: ${eth_price}")

        print(f"Buying {btc_amount} of bitcoin...")
        print(f"Buying {eth_amount} of ethereum...")

        btc_response = requests.post(url,
                                    data=None,
                                    headers=btc_request_headers)
        btc_order = btc_response.json()
        eth_response = requests.post(url,
                                    data=None,
                                    headers=eth_request_headers)
        eth_order = eth_response.json()

        limitBuyOrderCreated = True

        print(btc_order)
        print(eth_order)
    else:
        limitBuyOrderCreated = False
        

    time.sleep(60)  # wait for 1 minute
