from util.logger import logger
import uvicorn
from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    Request,
    Response,
    HTTPException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
import nft.score_api as score_api
import stake.stake_api as stake_api
from common.database import SessionLocal, init_db
import util.response_util as response_util
import traceback

app = None

app = FastAPI()


origins = ["http://localhost", "http://127.0.0.1", "0.0.0.0", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    logger.exception(exc)
    logger.error(f"Exception: {request.method} URL:{request.url}")


@app.get("/")
async def home():
    return {"message": "ok"}


router = APIRouter()
router.include_router(score_api.router, prefix="/score", tags=["score"])
router.include_router(stake_api.router, prefix="/stake", tags=["stake"])

app.include_router(router)

init_db()
logger.info("stake server start...")

uvicorn.run(app, host="0.0.0.0", port=8088)
