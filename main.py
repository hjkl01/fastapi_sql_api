from importlib import reload
import json
from datetime import datetime

import uvicorn
from dynaconf import Dynaconf
import redis
import pymongo
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from loguru import logger

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5000",
]

middleware = [Middleware(CORSMiddleware, allow_origins=origins)]

app = FastAPI(middleware=middleware)

security = HTTPBasic()

Config = Dynaconf(settings_files=[".secrets.toml"])


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, Config.user)
    correct_password = secrets.compare_digest(credentials.password, Config.password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


#  @app.post("/")
async def index():
    return {"Hello": "World !"}


#  @app.post("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


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

    async def redis_lpush(
        self, item: RedisItem, username: str = Depends(get_current_username)
    ) -> dict:
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
    async def redis_rpop(
        item: RedisItem, username: str = Depends(get_current_username)
    ) -> dict:
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


class MongoItem(BaseModel):
    db: str = "test"
    tablename: str = "tablename"
    query: dict = None
    limit: int = 1
    values: dict = None


class MongoAPI:
    def __init__(self) -> None:
        pass

    def connect_mongo(self, db="db", tablename="tablename"):
        mgclient = pymongo.MongoClient(Config.MONGO_URI)
        mgdb = mgclient[db]
        mgcol = mgdb[tablename]
        return mgclient, mgcol

    async def mongo_insert(
        self, item: MongoItem, username: str = Depends(get_current_username)
    ) -> dict:
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
            "result": item.values,
        }

    async def mongo_query(
        self, item: MongoItem, username: str = Depends(get_current_username)
    ) -> dict:
        logger.info(item)
        mgclient, mgcol = self.connect_mongo(db=item.db, tablename=item.tablename)
        # values = {"abr": 1}
        result = [q for q in mgcol.find(item.query, item.values).limit(item.limit)]
        mgclient.close()
        return {
            "success": "OK",
            "created_at": datetime.now(),
            "result": result,
        }

    #  def update(self, _id, _key, data):
    #      myquery = {"id": _id}
    #      newvalues = {"$set": {_key: data}}
    #      self.mycol.update_one(myquery, newvalues)
    #      logger.info(f"update success {_id}")
    #      return True


app.add_api_route("/", index)
app.add_api_route("/user/me/", read_current_user)
redis_api = RedisAPi()
app.add_api_route("/redis/lpush/", redis_api.redis_lpush, methods=["POST"])
app.add_api_route("/redis/rpop/", redis_api.redis_rpop, methods=["POST"])
mongo_api = MongoAPI()
app.add_api_route("/mongo/insert/", mongo_api.mongo_insert, methods=["POST"])
app.add_api_route("/mongo/query/", mongo_api.mongo_query, methods=["POST"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        debug=True,
        reload=True,
        host="0.0.0.0",
        port=6380,
        log_level="debug",
    )
