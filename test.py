import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

url = "http://localhost:8000/users/me"

host = "localhost"
urls = [
    f"http://{host}:8000/lpush/1/testkey/testvalue",
    f"http://{host}:8000/lpop/1/testkey",
]
for i in range(1000):
    for url in urls:
        resp = requests.post(
            url, auth=HTTPBasicAuth(os.getenv("user"), os.getenv("password"))
        )
        print(resp.status_code, i, resp.json())
