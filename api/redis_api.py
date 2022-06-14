import json
from datetime import datetime

import redis
from pydantic import BaseModel, typing
from fastapi import Depends

from .user_api import get_current_username
from settings import Config, logger


class RedisItem(BaseModel):
    db: int
    key: str
    values: typing.Any


class RedisAPI:
    def __init__(self) -> None:
        pass

    def connect_redis(self, db):
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
        r.lpush(item.key, json.dumps(item.values, ensure_ascii=False))
        length = r.llen(item.key)
        r.close()

        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": item.values,
            "length": length,
        }

    #  @app.post("/redis/rpop/")
    async def redis_rpop(self, item: RedisItem, username: str = Depends(get_current_username)) -> dict:
        logger.info("redis_rpop: {}".format(item))
        result = {"success": "OK", "created_at": datetime.now(), "result": None}
        try:
            r = self.connect_redis(item.db)
            res = json.loads(r.rpop(item.key))
            length = r.llen(item.key)
            r.close()
            result["result"] = res
            result["length"] = length
            return result
        except Exception as err:
            logger.error(err)
            return result
