import os
import json

from loguru import logger
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()


host = "127.0.0.1"

urls = [
    f"http://{host}:8000/lpush/",
    f"http://{host}:8000/rpop/",
]
for i in range(3):
    for url in urls:
        print(url)
        value = {f"dslakjdlksa{i}": f"dsljakdjsal{i}"}
        data = {"db": 3, "key": "test", "value": value}
        resp = requests.post(
            url,
            data=json.dumps(data, ensure_ascii=False),
            auth=HTTPBasicAuth(os.getenv("user"), os.getenv("password")),
        )
        logger.info(f"{resp.status_code}, {i}, {resp.json()}")
