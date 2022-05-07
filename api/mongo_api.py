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
    limit: int = 1
    skip: int = 0


class MongoAPI:
    def __init__(self) -> None:
        pass

    def connect_mongo(self, db="db", tablename="tablename"):
        mgclient = pymongo.MongoClient(Config.MONGO_URI)
        mgdb = mgclient[db]
        mgcol = mgdb[tablename]
        return mgclient, mgcol

    async def mongo_insert(self, item: MongoItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(item)
        mgclient, mgcol = self.connect_mongo(db=item.db, tablename=item.tablename)
        #  mgol.save(item.values)
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
        mgclient.close()
        return {
            "success": "OK" if result is None else "NG",
            "result": result,
            "created_at": datetime.now(),
        }

    async def mongo_query(self, item: MongoItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(item)
        mgclient, mgcol = self.connect_mongo(db=item.db, tablename=item.tablename)
        # values = {"abr": 1}
        _limit = item.limit
        if item.limit > 100 or item.limit is None or item.limit is False or item.limit == 0:
            _limit = 100
        result = [q for q in mgcol.find(item.query, item.values).limit(_limit).skip(item.skip)]
        mgclient.close()
        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": json.loads(json.dumps(result, default=str)),
        }

    async def mongo_update(self, item: MongoItem, username: str = Depends(get_current_username)):
        logger.info(item)
        mgclient, mgcol = self.connect_mongo(db=item.db, tablename=item.tablename)

        result = None
        try:
            #  myquery = { "name": { "$regex": "^F" } }
            #  newvalues = {"$set": {"comments": "values"}}
            mgcol.update(item.query, item.values)
        except Exception as err:
            logger.info(err)
            result = str(err)
        mgclient.close()
        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": result,
        }
