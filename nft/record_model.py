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


class RecordModel(Base):
    __tablename__ = "redeem_record"
    sid = Column(BigInteger, primary_key=True, autoincrement=True)
    address = Column(String(128), default="", unique=True)
    score = Column(Integer, default=0)
    redeemIslandtimes = Column(Integer, default=0)
    redeemRewardtimes = Column(Integer, default=0)
    redeemScoreCount = Column(Integer, default=0)
    preRewardScore = Column(Integer, default=0)
    lastRedeemTime = Column(DateTime, default=0)

    def to_dict(self):
        return {
            "sid": self.sid,
            "address": self.address,
            "score": self.score,
            "redeemIslandtimes": self.redeemIslandtimes,
            "redeemRewardtimes": self.redeemRewardtimes,
            "redeemScoreCount": self.redeemScoreCount,
            "preRewardScore": self.preRewardScore,
            "lastRedeemTime": self.lastRedeemTime,
        }


def save_record(record):
    SessionLocal().add(record)


def get_record(address):
    record = (
        SessionLocal().query(RecordModel).filter(RecordModel.address == address).first()
    )
    return record


def get_record_list(page=0, page_size=20):
    session = SessionLocal()

    # conditions = [RecordModel.address == address]
    query = session.query(RecordModel)
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


def update_record_by_id(rid, dict_data) -> None:
    SessionLocal().query(RecordModel).filter(RecordModel.rid == rid).update(dict_data)


def del_record(rid) -> None:
    SessionLocal().query(RecordModel).filter(RecordModel.rid == rid).delete()
