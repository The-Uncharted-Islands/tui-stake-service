from util.logger import logger
import json
from web3 import Web3
from eth_account import Account
from eth_utils.hexadecimal import encode_hex
from eth_account.messages import encode_defunct
from nft.reward_model import *
from nft.record_model import *
from datetime import datetime, timedelta
import requests

game_server_api_key = ""


def issue(reward: RewardModel):
    return
    try:
        itemId = reward.itemId
        amount = reward.amount
        # game_server_api_key
        url = f"https://xxx?address={address} "
        response = requests.get(url)
        result = response.json()
        # logger.info(result)
        if "success" in result:
            reward.issued = 1
            reward.issuedTime = datetime.now()
    except Exception as e:
        pass

    pass
