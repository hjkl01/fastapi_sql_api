import uvicorn
from fastapi import Depends, FastAPI

from api.user_api import get_current_username
from api.redis_api import RedisAPi
from api.mongo_api import MongoAPI
from api.mysql_api import mysql_api

app = FastAPI()

redis_api = RedisAPi()
mongo_api = MongoAPI()


async def index():
    return {"Hello": "World !"}


async def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}


app.add_api_route("/", index)
app.add_api_route("/api/user/me/", read_current_user)
app.add_api_route("/api/redis/lpush/", redis_api.redis_lpush, methods=["POST"])
app.add_api_route("/api/redis/rpop/", redis_api.redis_rpop, methods=["POST"])
app.add_api_route("/api/mongo/insert/", mongo_api.mongo_insert, methods=["POST"])
app.add_api_route("/api/mongo/query/", mongo_api.mongo_query, methods=["POST"])
app.add_api_route("/api/mongo/update/", mongo_api.mongo_update, methods=["POST"])
app.add_api_route("/api/mysql/query/", mysql_api, methods=["POST"])


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True, host="0.0.0.0", port=6380, log_level="debug")
