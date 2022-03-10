import json
from datetime import datetime

import redis
from pydantic import BaseModel
from fastapi import Depends

from .user_api import get_current_username
from settings import Config, logger


class RedisItem(BaseModel):
    db: int
    key: str
    value = ""


class RedisAPi:
    def __init__(self) -> None:
        pass

    async def connect_redis(self, db):
        r = redis.Redis(
            host=Config.redis_host,
            port=Config.redis_port,
            password=Config.redis_password,
            db=db,
        )
        return r

    async def redis_lpush(self, item: RedisItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(f"redis_lpush: {item}")
        r = self.connect_redis(item.db)
        r.lpush(item.key, json.dumps(item.value, ensure_ascii=False))
        length = r.llen(item.key)
        r.close()

        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": item.value,
            "length": length,
        }

    #  @app.post("/redis/rpop/")
    async def redis_rpop(self, item: RedisItem, username: str = Depends(get_current_username)) -> dict:
        logger.info("redis_rpop: {}".format(item))
        r = self.connect_redis(item.db)
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
