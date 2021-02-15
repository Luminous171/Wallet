import subprocess # Library for using the terminal
import os
from dotenv import load_dotenv
import json
from constants import *
import bit
import web3
from web3 import Web3
from bit.network import NetworkAPI
from eth_account import Account
from web3.middleware import geth_poa_middleware

# Load .env enviroment variables and mnemomic
load_dotenv()
mnemonic = os.getenv('MNEMONIC')

# Function used to derive wallet keys from master key
def derive_wallets(mnemonic,Coin,Numderive):

    # For Windows users the php derive part replaces ./derive
    command = f'php derive -g --mnemonic="{mnemonic}" --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --coin={Coin} --numderive={Numderive} --format=json'

    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, error) = p.communicate()
    p_status = p.wait()

    # print(output)
    keys = json.loads(output)
    return keys

coins = {}
types = [BTCTEST,ETH]

for type in types:
    coins[type] = derive_wallets(Mnemonic, type, 3)
    

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Function used to convert key to account
def priv_key_to_account(coin,priv_key):
    if coin == BTCTEST:
        return bit.PrivateKeyTestnet(priv_key)
    elif coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    else:
        print('Must use either BTCTEST or ETH')

# Function used to create a transaction
def create_tx(coin,account,to,amount):
    if coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to,amount, BTC)])
    elif coin == ETH:
        
        
        gas_estimate = w3.eth.estimateGas(
            {'from': account.address, 'to': to, 'value': amount}
        )

        return {
            'from': account.address,
            'to': to,
            'value': amount,
            'gasPrice': w3.eth.gasPrice,
            'gas': gas_estimate,
            'nonce': w3.eth.getTransactionCount(account.address)
        }
    else:
        print('Must use either BTCTEST or ETH')

# Function used to send transaction
def send_tx(coin,account,to,amount):
    if coin == BTCTEST:
        raw_tx = create_tx(coin,account,to,amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)
    elif coin == ETH:
        raw_tx = create_tx(coin,account,to,amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    else:
        print('Must use either BTCTEST or ETH')   
