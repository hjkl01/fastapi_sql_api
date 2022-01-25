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

#  app = FastAPI()
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


@app.post("/")
async def index():
    return {"Hello": "World !"}


@app.post("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


class RedisItem(BaseModel):
    db: int
    key: str
    value: dict = None


@app.post("/redis/lpush/")
async def redis_lpush(
    item: RedisItem, username: str = Depends(get_current_username)
) -> dict:
    logger.info(item)
    r = redis.Redis(
        host=Config.redis_host,
        port=Config.redis_port,
        password=Config.redis_password,
        db=item.db,
    )
    r.lpush(item.key, json.dumps(item.value, ensure_ascii=False))
    length = r.llen(item.key)
    r.close()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": item.value,
        "length": length,
    }


@app.post("/redis/rpop/")
async def redis_rpop(
    item: RedisItem, username: str = Depends(get_current_username)
) -> dict:
    r = redis.Redis(
        host=Config.redis_host,
        port=Config.redis_port,
        password=Config.redis_password,
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


class MongoAPI:
    def __init__(self, db="db", tablename="tablename"):
        self.uri = Config.MONGO_URI
        self.myclient = pymongo.MongoClient(self.uri)
        mydb = self.myclient[db]
        self.mycol = mydb[tablename]

    # values = {"abr": 1}
    def query(self, myquery={"name": "somename"}, values=None):
        return [q for q in self.mycol.find(myquery, values)]

    def save(self, data):
        try:
            self.mycol.insert_one(data)
            logger.info("save success ", data)
            return True
        except Exception as err:
            if "duplicate key" in str(err):
                logger.info("duplicate key")
            else:
                logger.info(err)
                return False

    def update(self, _id, _key, data):
        myquery = {"id": _id}
        newvalues = {"$set": {_key: data}}
        self.mycol.update_one(myquery, newvalues)
        logger.info(f"update success {_id}")
        return True

    def quit(self):
        self.myclient.close()


class MongoItem(BaseModel):
    db: str = "test"
    tablename: str = "tablename"
    query: dict = None
    values: dict = None


@app.post("/mongo/insert/")
async def mongo_insert(
    item: MongoItem, username: str = Depends(get_current_username)
) -> dict:
    logger.info(item)
    mongoapi = MongoAPI(db=item.db, tablename=item.tablename)
    mongoapi.save(item.values)
    mongoapi.quit()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": item.values,
    }


@app.post("/mongo/query/")
async def mongo_query(
    item: MongoItem, username: str = Depends(get_current_username)
) -> dict:
    logger.info(item)
    mongoapi = MongoAPI(db=item.db, tablename=item.tablename)
    result = mongoapi.query(myquery=item.query, values=item.values)
    mongoapi.quit()
    return {
        "success": "OK",
        "created_at": datetime.now(),
        "result": result,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", debug=True, port=6380, log_level="debug")
