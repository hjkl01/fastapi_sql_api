import json
import time
from threading import Thread

from dynaconf import Dynaconf
from loguru import logger
import requests
from requests.auth import HTTPBasicAuth


Config = Dynaconf(settings_files=[".secrets.toml"])


def send_request(url, data):
    print(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    resp = requests.post(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        auth=HTTPBasicAuth(Config.user, Config.password),
    )
    logger.info(f"{resp.status_code}, {resp.json()}")
    return resp


def redis_test():
    urls = [
        f"http://{Config.host}/redis/lpush/",
        f"http://{Config.host}/redis/rpop/",
    ]
    for i in range(3):
        for url in urls:
            print(url)
            value = {f"dslakjdlksa{i}": f"dsljakdjsal{i}"}
            value = {f"广州{i}": f"dsljakdjsal{i}"}
            data = {"db": 3, "key": "test", "value": value}
            t = Thread(
                target=send_request,
                args=(
                    url,
                    data,
                ),
            )
            t.start()
            time.sleep(0.1)


def mongo_test_insert():
    # insert
    url = f"http://{Config.host}/mongo/insert/"
    for i in range(10):
        print(url)
        db = "test"
        tablename = "tablename"
        values = {"_id": i, "values": f"value_{i}"}
        data = {"db": db, "tablename": tablename, "values": values}
        t = Thread(
            target=send_request,
            args=(
                url,
                data,
            ),
        )
        t.start()
        time.sleep(0.1)


def mongo_test_query():
    # query
    url = f"http://{Config.host}/mongo/query/"
    data = {
        "db": "test",
        "tablename": "tablename",
        "query": None,
        #  "query": {"_id": "1"},
        "values": {"_id": 1},
        #  "values": None,
        "limit": 10,
        #  "limit": False,
    }
    resp = send_request(url, data=data)
    print(resp.status_code)
    print(resp.json())


if __name__ == "__main__":
    #  redis_test()
    #  mongo_test_insert()
    mongo_test_query()
