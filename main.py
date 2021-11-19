import os
from datetime import datetime

import redis
import secrets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

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


@app.post("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


@app.post("/lpush/{db}/{key}/{value}")
async def redis_lpush(
    db: int,
    key: str,
    value: str,
    username: str = Depends(get_current_username),
) -> dict:
    r = redis.Redis(
        host=os.getenv("redis_host"),
        port=os.getenv("redis_port"),
        password=os.getenv("redis_password"),
        db=db,
    )
    r.lpush(key, value)
    length = r.llen(key)
    r.close()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": None,
        "length": length,
    }


@app.post("/lpop/{db}/{key}")
async def redis_lpop(
    db: int,
    key: str,
    username: str = Depends(get_current_username),
) -> dict:
    r = redis.Redis(
        host=os.getenv("redis_host"),
        port=os.getenv("redis_port"),
        password=os.getenv("redis_password"),
        db=db,
    )
    result = r.lpop(key)
    length = r.llen(key)
    r.close()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": result,
        "length": length,
    }
