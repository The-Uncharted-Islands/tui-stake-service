from fastapi import APIRouter, Depends, Request, HTTPException
from eth_account import Account
from eth_account.messages import (
    encode_structured_data,
    encode_typed_data,
    encode_defunct,
)
from web3 import Web3
from setting import (
    signer,
    API_KEY,
    tui_address,
    deposit_address,
    stake_address,
    lp_address,
    weth_address,
    chain_id,
    eth_provider,
)
import util.response_util as response_util
from util.logger import logger
import datetime
import json
import requests

router = APIRouter()


info_data = {
    "stakeContract": stake_address,
    "assetPool": deposit_address,
    "lpToken": lp_address,
    "tuiToken": tui_address,
    "chainId": chain_id,
    "lpPrice": 0,
}

lp_update_time = None


@router.get("/info")
def info():
    global lp_update_time
    now = datetime.datetime.now()

    if lp_update_time == None:
        lp_price_update()
        lp_update_time = now
    else:
        diff = now - lp_update_time
        if diff.seconds > 600:
            lp_price_update()
            lp_update_time = now

    return response_util.success(info_data)

eth_client = Web3(Web3.HTTPProvider(eth_provider))

eth_lp_address = Web3.to_checksum_address("0x")
with open("file/lp.json") as f:
    lp_abi = json.load(f)
    lp_contract = eth_client.eth.contract(address=eth_lp_address, abi=lp_abi)

with open("file/erc20_standard.json") as f:
    erc20_abi = json.load(f)
    # weth
    token1_contract = eth_client.eth.contract(
        address="0x", abi=erc20_abi
    )
    # tui
    token0_contract = eth_client.eth.contract(
        address="0x", abi=erc20_abi
    )


def lp_price_update():
    liquidity = 1
    _totalSupply = lp_contract.functions.totalSupply().call()
    balance0 = token0_contract.functions.balanceOf(eth_lp_address).call()
    balance1 = token1_contract.functions.balanceOf(eth_lp_address).call()
    logger.info(f"balance0 {balance0} balance1 {balance1}")

    amount0 = liquidity * balance0 / _totalSupply
    amount1 = liquidity * balance1 / _totalSupply

    logger.info(f"amount0 {amount0} amount1 {amount1}")
    # amount1 * weth price
    # amount0 * tui price
    tui_price = get_tui_price()
    weth_price = get_weth_price()
    lp_price = amount1 * weth_price + amount0 * tui_price
    logger.info(f"lp_price {lp_price} tui_price {tui_price} weth_price {weth_price}")
    info_data["lpPrice"] = lp_price
    return lp_price


def get_tui_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tui&vs_currencies=usd"
    response = requests.get(url)
    result = response.json()
    return result["tui"]["usd"]


def get_weth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=weth&vs_currencies=usd"
    response = requests.get(url)
    result = response.json()
    return result["weth"]["usd"]

