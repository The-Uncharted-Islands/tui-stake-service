from util.logger import logger
import json
from web3 import Web3
from eth_account import Account
from eth_utils.hexadecimal import encode_hex
from eth_account.messages import encode_defunct
from nft.reward_model import *
from nft.record_model import *
from datetime import datetime, timezone, timedelta
import random
import nft.reward_issue as reward_issue


redeem_score_cost = [
    20000,
    40000,
    60000,
    80000,
    100000,
    150000,
    200000,
    250000,
    300000,
    350000,
    400000,
    450000,
    500000,
    550000,
    600000,
    650000,
    700000,
    800000,
    900000,
    1000000,
]


item1 = {"rewardId": 1, "name": "史诗岛屿盲盒*1", "rate": 0}

reward_items = [
    {"rewardId": 2, "name": "珠果种子*3", "rate": 28},
    {"rewardId": 3, "name": "自然水晶*5000", "rate": 15},
    {"rewardId": 4, "name": "积分*2000", "rate": 10},
    {"rewardId": 5, "name": "普通岛屿盲盒*1", "rate": 2},
    {"rewardId": 6, "name": "食物*3", "rate": 30},
    {"rewardId": 7, "name": "初级种子盲盒*3", "rate": 10},
    {"rewardId": 8, "name": "晶石*10", "rate": 5},
]

total_rate = 0
for item in reward_items:
    total_rate = total_rate + item["rate"]


def apply_reward(address, reward: RewardModel, record: RecordModel):
    rewardId = reward.rewardId
    itemId = 0
    amount = 0
    if rewardId == -1:
        island_type = random_choose([0, 1, 2, 3], False)
        rarityIdx = random_choose(
            [
                {"rarityIdx": 0, "rate": 30},
                {"rarityIdx": 1, "rate": 60},
                {"rarityIdx": 2, "rate": 10},
            ],
            True,
        )["rarityIdx"]

        # islands[island_type][rarityIdx]
        islands = []
        islands.append([412, 413, 414]) 
        islands.append([422, 423, 424])  
        islands.append([432, 433, 434]) 
        islands.append([442, 443, 444]) 
        itemId = islands[island_type][rarityIdx]
        amount = 1
    elif rewardId == 1:
        itemIds = [414, 424, 434, 444]
        itemId = random_choose(itemIds, False)
        amount = 1
    elif rewardId == 2:
        itemId = 301
        amount = 3
    elif rewardId == 3:
        itemId = 2
        amount = 5000
    elif rewardId == 4:
        pass
    elif rewardId == 5:
        island_type = random_choose([0, 1, 2, 3], False)
        rarityIdx = random_choose(
            [
                {"rarityIdx": 0, "rate": 30},
                {"rarityIdx": 1, "rate": 30},
                {"rarityIdx": 2, "rate": 40},
            ],
            True,
        )["rarityIdx"]

        # islands[island_type][rarityIdx]
        islands = []
        islands.append([411, 412, 413])
        islands.append([421, 422, 423])
        islands.append([431, 432, 433])
        islands.append([441, 442, 443])
        itemId = islands[island_type][rarityIdx]
        amount = 1
    elif rewardId == 6:
        itemId = 101
        amount = 3
    elif rewardId == 7:
        itemId = 201
        amount = 3
    elif rewardId == 8:
        itemId = 102
        amount = 10

    reward.itemId = itemId
    reward.amount = amount
    reward_issue.issue(reward)


def create_reward_item(address: str, redeemType, rewardId, scoreUse: int):

    reward = RewardModel()
    reward.address = address
    reward.redeemType = redeemType
    reward.rewardId = rewardId
    reward.scoreUse = scoreUse
    reward.redeemTime = datetime.now()
    save_reward(reward)

    return reward


def random_reward_id(address: str, currentRoundScore: int):
    rnd = random.random() * total_rate
    t = 0
    idx = 0
    for item in reward_items:
        t = t + item["rate"]
        if t > rnd:
            break
        idx = idx + 1

    rewardId = reward_items[idx]["rewardId"]
    return create_reward_item(address, 2, rewardId, currentRoundScore)


def redeem_island(address: str, currentRoundScore: int):
    rewardId = -1
    return create_reward_item(address, 1, rewardId, currentRoundScore)


def get_redeem_record(address: str, score=-1):
    record = get_record(address)
    if record == None:
        record = RecordModel()
        record.address = address

        record.redeemIslandtimes = 0
        record.redeemRewardtimes = 0
        record.redeemScoreCount = 0
        record.preRewardScore = 0
        record.lastRedeemTime = datetime.now()
        save_record(record)

    if score != -1:
        record.score = score
    SessionLocal().commit()

    return record


def is_same_day(timestamp1, timestamp2):
    d1 = datetime.fromtimestamp(int(timestamp1), tz=timezone.utc)
    d2 = datetime.fromtimestamp(int(timestamp2), tz=timezone.utc)
    return d1.date() == d2.date() and abs(d1 - d2) <= timedelta(hours=24)


def random_choose(data_list, useRate=True):
    if useRate:
        t_r = 0
        for item in data_list:
            t_r = t_r + item["rate"]
        rnd = random.random() * t_r
        t = 0
        idx = 0
        for item in data_list:
            t = t + item["rate"]
            if t > rnd:
                break
            idx = idx + 1

        return data_list[idx]

    else:
        t_r = len(data_list)
        idx = int(random.random() * t_r)
        return data_list[idx]


def verify(address, msg: str, signature: str):
    if address == None or msg == None or signature == None:
        return False

    saddress = str(address)
    msg = f"TheUnchartedIslands want to login with your wallet address:\n{saddress}"
    message = encode_defunct(text=msg)
    address_recover = Account.recover_message(message, signature=signature)
    logger.info(f"msg {msg} address_recover{address_recover}")
    return address == address_recover
