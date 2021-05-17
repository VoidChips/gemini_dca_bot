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
    amount *= 0.98  # make it a little smaller because of round up
    amount = round(amount, 6)
    return amount

# get the api keys from config.py
gemini_api_key = config.gemini_api_key
gemini_api_secret = config.gemini_api_secret

base_url = "https://api.gemini.com"
endpoint = "/v1/order/new"
url = base_url + endpoint

# get btc's price and convert to float
response = requests.get(base_url + "/v1/pubticker/btcusd")
btc_data = response.json()
btc_price = float(btc_data['last'])

# get eth's price and convert to float
response = requests.get(base_url + "/v1/pubticker/ethusd")
eth_data = response.json()
eth_price = float(eth_data['last'])

# get the amount of fiat balance
t = datetime.datetime.now()
payload_nonce_value = int(time.mktime(t.timetuple())*1000)
payload_nonce = str(payload_nonce_value)

balance_payload = {
    "nonce": payload_nonce,
    "request": base_url + "/v1/balances"
}
encoded_payload = json.dumps(balance_payload).encode()
b64 = base64.b64encode(encoded_payload)
signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()
request_headers = {'Content-Type': "text/plain",
                       'Content-Length': "0",
                       'X-GEMINI-APIKEY': gemini_api_key,
                       'X-GEMINI-PAYLOAD': b64,
                       'X-GEMINI-SIGNATURE': signature,
                       'Cache-Control': "no-cache"}
response = requests.post(url,
                         data=None,
                         headers=request_headers)
balance_data = response.json()
balance = balance_data

# get the amount of bitcoin and ethereum that will be purchased
btc_amount = fiatToCrypto(40.0, btc_price)
eth_amount = fiatToCrypto(40.0, eth_price)

payload_nonce_value += 1  # nonce cannot repeat and must increase
payload_nonce = str(payload_nonce_value)

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

payload_nonce_value += 1
payload_nonce = str(payload_nonce_value)

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

# buy on sundays
if weekday == 6:
    # display current price of btc and eth
    print(f"BTC: ${btc_price}")
    print(f"ETH: ${eth_price}")
    print(f"Balance: ${balance_data}")

    print(f"Buying {btc_amount} of bitcoin...")
    print(f"Buying {eth_amount} of ethereum...")

    btc_response = requests.post(url,
                                 data=None,
                                 headers=btc_request_headers)
    btc_order = btc_response.json()

    # time.sleep(1)  # wait for 1 second

    eth_response = requests.post(url,
                                 data=None,
                                 headers=eth_request_headers)
    eth_order = eth_response.json()
    
    print(btc_order)
    print(eth_order)
