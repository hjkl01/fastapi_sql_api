import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

url = "http://localhost:8000/users/me"

urls = [
    "http://localhost:8000/lpush/0/testkey/testvalue",
    "http://localhost:8000/lpop/0/testkey/",
]
for url in urls:
    resp = requests.post(
        url, auth=HTTPBasicAuth(os.getenv("user"), os.getenv("password"))
    )
    print(resp.status_code)
    print(resp.json())
