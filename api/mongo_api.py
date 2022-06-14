import json
from datetime import datetime

import pymongo
from pydantic import BaseModel
from fastapi import Depends

from settings import Config, logger
from .user_api import get_current_username


class MongoItem(BaseModel):
    db: str = "test"
    tablename: str = "tablename"
    query: dict = None
    values: dict = None
    limit: int = 100
    skip: int = 0


class MongoAPI:
    def __init__(self) -> None:
        self.mgclient = None

    def connect_mongo(self):
        self.mgclient = pymongo.MongoClient(Config.MONGO_URI, maxPoolSize=100)
        return self.mgclient

    def insert_api(self, item: MongoItem):
        if not self.mgclient:
            self.mgclient = self.connect_mongo()
        mgcol = self.mgclient[item.db][item.tablename]

        result = None
        try:
            mgcol.insert_one(item.values)
            logger.info("save success ", item.values)
        except Exception as err:
            if "duplicate key" in str(err):
                logger.info("duplicate key")
                result = "duplicate key"
            else:
                logger.info(err)
                result = err
        return result

    def query_api(self, item: MongoItem):
        if not self.mgclient:
            self.mgclient = self.connect_mongo()
            logger.warning('mongo re connect')
        mgcol = self.mgclient[item.db][item.tablename]

        # values = {"abr": 1}
        _limit = item.limit
        if item.limit > 100 or item.limit is None or item.limit is False or item.limit == 0:
            _limit = 100
        result = [q for q in mgcol.find(item.query, item.values).limit(_limit).skip(item.skip)]
        return result

    async def mongo_insert(self, item: MongoItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(item)
        result = self.insert_api(item)
        return {
            "success": "OK" if result is None else "NG",
            "result": result,
            "created_at": datetime.now(),
        }

    async def mongo_query(self, item: MongoItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(item)
        result = self.query_api(item)
        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": json.loads(json.dumps(result, default=str)),
        }

    async def mongo_update(self, item: MongoItem, username: str = Depends(get_current_username)):
        logger.info(item)
        if not self.mgclient:
            self.mgclient = self.connect_mongo()
        mgcol = self.mgclient[item.db][item.tablename]

        result = None
        try:
            #  myquery = { "name": { "$regex": "^F" } }
            #  newvalues = {"$set": {"comments": "values"}}
            mgcol.update(item.query, item.values)
        except Exception as err:
            logger.info(err)
            result = str(err)
        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": result,
        }

    async def mongo_delete(self, item: MongoItem, username: str = Depends(get_current_username)):
        logger.info(item)
        if not self.mgclient:
            self.mgclient = self.connect_mongo()
        mgcol = self.mgclient[item.db][item.tablename]

        result = None
        try:
            #  myquery = { "name": { "$regex": "^F" } }
            #  newvalues = {"$set": {"comments": "values"}}
            mgcol.update(item.query, item.values)
        except Exception as err:
            logger.info(err)
            result = str(err)
        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": result,
        }
