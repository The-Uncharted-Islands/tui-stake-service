from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import Union
from util import response_util
from util.logger import logger
from web3 import Web3
from datetime import datetime, timedelta
from common.database import SessionLocal
import requests
import time

import service.score_service as score_service

router = APIRouter()

data = {}

sign_msg = ""


class Redeem(BaseModel):
    address: str
    sig: str


@router.post("/redeemIsland")
def redeem_island(redeem: Redeem):
    address: str = redeem.address
    sig: str = redeem.sig
    cast_address = Web3.to_checksum_address(address)
    logger.info(f"redeem island address: {address} {sig}")
    s_address = str(cast_address)
    return response_util.fail("The Phase 1 Island Redemption Event has concluded.")

    if not score_service.verify(s_address, sign_msg, sig):
        return response_util.fail("sig error")

    score = fetch_score(s_address)
    record = score_service.get_redeem_record(s_address, score)
    if record.score > score:
        score = record.score

    if record.redeemIslandtimes >= 3:
        return response_util.fail("Limit maximum of 3 times")

    availableScore = score - record.redeemScoreCount - record.redeemIslandtimes * 300000
    # availableScore = 2000000
    if availableScore < 300000:
        return response_util.fail("Insufficient points")

    reward = score_service.redeem_island(s_address, 300000)

    record.redeemIslandtimes = record.redeemIslandtimes + 1
    record.lastRedeemTime = datetime.now()

    score_service.apply_reward(s_address, reward, record)

    score_service.save_record(record)
    score_service.save_reward(record)

    SessionLocal().commit()
    data = {"record": record.to_dict(), "reward": reward.to_dict()}
    return response_util.success(data)


@router.post("/redeem")
def redeem(redeem: Redeem):

    address: str = redeem.address
    sig: str = redeem.sig

    cast_address = Web3.to_checksum_address(address)
    logger.info(f"redeem address: {address} {sig}")
    s_address = str(cast_address)
    # check sig
    if not score_service.verify(s_address, sign_msg, sig):
        return response_util.fail("sig error")
    # get score
    score = fetch_score(s_address)
    record = score_service.get_redeem_record(s_address, score)
    if record.score > score:
        score = record.score

    now = int(time.time())

    if not score_service.is_same_day(now, datetime.timestamp(record.lastRedeemTime)):
        record.redeemRewardtimes = 0
    redeem_score_cost_len = len(score_service.redeem_score_cost)
    if redeem_score_cost_len != 20:
        logger.error("data error redeem_score_cost len {redeem_score_cost_len}")
    if (
        record.redeemRewardtimes >= redeem_score_cost_len
        or record.redeemRewardtimes >= 20
    ):
        return response_util.fail("Limit maximum 20 times per day")

    currentRoundScore = score_service.redeem_score_cost[record.redeemRewardtimes]
    availableScore = score - record.redeemScoreCount - record.redeemIslandtimes * 300000
    if availableScore < currentRoundScore:
        return response_util.fail("Insufficient points")

    currentScoreRedeem = record.redeemScoreCount - record.preRewardScore

    reward = None
    if currentScoreRedeem > 10000000:
        reward = score_service.create_reward_item(s_address, 2, 1, currentRoundScore)
        record.preRewardScore = record.preRewardScore + 10000000
    else:
        reward = score_service.random_reward_id(s_address, currentRoundScore)

    record.redeemRewardtimes = record.redeemRewardtimes + 1
    record.redeemScoreCount = currentRoundScore + record.redeemScoreCount
    record.lastRedeemTime = datetime.now()

    score_service.apply_reward(s_address, reward, record)

    score_service.save_record(record)
    score_service.save_reward(record)

    SessionLocal().commit()

    data = {"record": record.to_dict(), "reward": reward.to_dict()}
    return response_util.success(data)


@router.get("/get_redeem_record")
def get_redeem_record(address: str):
    cast_address = Web3.to_checksum_address(address)
    logger.info(f"get redeem record address: {address}")
    s_address = str(cast_address)

    record = score_service.get_redeem_record(s_address)
    now = int(time.time())

    if not score_service.is_same_day(now, datetime.timestamp(record.lastRedeemTime)):
        record.redeemRewardtimes = 0

    return response_util.success(record.to_dict())


@router.get("/get_reward_history")
def get_reward_history(address: str):
    cast_address = Web3.to_checksum_address(address)
    logger.info(f"get redeem history address: {address}")
    s_address = str(cast_address)
    (
        content,
        count,
    ) = score_service.get_reward_list(s_address, 0, 1000)
    reward_list = []
    for e in content:
        reward_list.append(e.to_dict())
    # SessionLocal().close()
    return response_util.success(reward_list)


def fetch_score(address):
    try:
        url = f"https://api.theUnchartedIslands.xyz/stake-info?address={address}"
        response = requests.get(url)
        result = response.json()
        # logger.info(result)
        if "data" in result and "summary_reward_points" in result["data"]:
            score = result["data"]["summary_reward_points"]
            return int(float(score))
    except Exception as e:
        pass

    return -1
