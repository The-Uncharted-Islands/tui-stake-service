from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    DECIMAL,
    BigInteger,
)
from sqlalchemy import func, or_, and_
from common.database import Base, SessionLocal
from util.logger import logger


class RewardModel(Base):
    __tablename__ = "redeem_reward"
    rid = Column(BigInteger, primary_key=True, autoincrement=True)
    address = Column(String(128), default="", index=True)
    scoreUse = Column(Integer, default=0)
    redeemType = Column(Integer, default=0)
    rewardId = Column(Integer, default=0)
    itemId = Column(Integer, default=0)
    amount = Column(Integer, default=0)
    issued = Column(Integer, default=0)
    redeemTime = Column(DateTime, default=0)
    issuedTime = Column(DateTime, default=0)

    def to_dict(self):
        return {
            "rid": self.rid,
            "address": self.address,
            "scoreUse": self.scoreUse,
            "redeemType": self.redeemType,
            "rewardId": self.rewardId,
            "itemId": self.itemId,
            "amount": self.amount,
            "issued": self.issued,
            "redeemTime": self.redeemTime,
            "issuedTime": self.issuedTime,
        }


def save_reward(reward):
    SessionLocal().add(reward)


def get_reward_list(address, page=0, page_size=20):
    session = SessionLocal()

    conditions = [RewardModel.address == address]
    query = session.query(RewardModel).filter(*conditions)
    count = query.count()
    if page_size:
        query = query.limit(page_size)
    if page:
        query = query.offset(page * page_size)

    content = query.all()

    return (
        content,
        count,
    )


def update_reward_by_id(rid, dict_data) -> None:
    SessionLocal().query(RewardModel).filter(RewardModel.rid == rid).update(dict_data)


def del_reward(rid) -> None:
    SessionLocal().query(RewardModel).filter(RewardModel.rid == rid).delete()
