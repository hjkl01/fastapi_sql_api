import os
import json
from datetime import datetime

import redis
import secrets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from loguru import logger

app = FastAPI()
security = HTTPBasic()
load_dotenv()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("user"))
    correct_password = secrets.compare_digest(
        credentials.password, os.getenv("password")
    )
    if not (correct_username and correct_password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.post("/")
async def index():
    return {"Hello": "World !"}


@app.post("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


class Item(BaseModel):
    db: int
    key: str
    value: dict = None


@app.post("/lpush/")
async def redis_lpush(
    item: Item,
    username: str = Depends(get_current_username),
) -> dict:
    logger.info(item)
    r = redis.Redis(
        host=os.getenv("redis_host", "redis"),
        port=os.getenv("redis_port", 6379),
        password=os.getenv("redis_password", "password"),
        db=item.db,
    )
    r.lpush(item.key, json.dumps(item.value, ensure_ascii=False))
    length = r.llen(item.key)
    r.close()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": None,
        "length": length,
    }


@app.post("/rpop/")
async def redis_rpop(
    item: Item,
    username: str = Depends(get_current_username),
) -> dict:
    r = redis.Redis(
        host=os.getenv("redis_host", "redis"),
        port=os.getenv("redis_port", 6379),
        password=os.getenv("redis_password", "password"),
        db=item.db,
    )
    result = r.rpop(item.key)
    if result:
        result = json.loads(result)
    length = r.llen(item.key)
    r.close()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": result,
        "length": length,
    }
