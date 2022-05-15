from web3 import Web3
from plyer import notification
import requests
import abis
import time
import json


def getAbi(x):
    return {
        'eth': abis.ethAbi,
        'bsc': abis.bscAbi,
        'avalanche': abis.avalancheAbi,
    }[x]


with open('config.json', "r") as f:
    config = json.load(f)

chain = config['chain']
node = config['node'].split('/')
node[4] = chain
node = '/'.join(node)
web3 = Web3(Web3.HTTPProvider(node))
print("Connection: {}".format(web3.isConnected()))

tokenAddress = config['tokenAddress']
apiUrl = config['apiUrl'].split('/')
apiUrl[6] = tokenAddress
apiUrl = '/'.join(apiUrl).split('=')
apiUrl[1] = chain
tokenPrice = '='.join(apiUrl)

abi = getAbi(chain)
contract = web3.eth.contract(address=tokenAddress, abi=abi)

name = contract.functions.name().call()
symbol = contract.functions.symbol().call()

headers = {
    'x-api-key': config['apiKey']
}

lowerBound = config['lowerBoundPrice']
upperBound = config['upperBoundPrice']
notifTimeout = 180  # seconds between the same bound notification
upperNotifTime = 0
lowerNotifTime = 0

while True:
    try:
        resp = requests.request("GET", tokenPrice, headers=headers)
    except ValueError:
        print("# Request error #")

    resp = resp.json()
    priceUSD = resp['usdPrice']
    print("{} - USD price: {:.2f}".format(time.strftime("%H:%M:%S", time.localtime()), priceUSD))

    if priceUSD >= upperBound:
        print("--- Upper bound price hit. ---")
        if time.time() - upperNotifTime > notifTimeout:
            upperNotifTime = time.time()
            notification.notify(
                title = 'Upper bound price hit.',
                message = 'Price: {:.2f}'.format(priceUSD),
                app_icon = 'icon/icon.ico',
                timeout = 5
            )
    elif priceUSD <= lowerBound:
        print("--- Lower bound price hit. ---")
        if time.time() - lowerNotifTime > notifTimeout:
            lowerNotifTime = time.time()
            notification.notify(
                title = 'Lower bound price hit.',
                message = 'Price: {:.2f}'.format(priceUSD),
                app_icon = 'icon/icon.ico',
                timeout = 5
            )

    time.sleep(1)