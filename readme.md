```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
pip install -r ./requirements.txt
cp .env.example .env
# update .env
uvicorn main:app

# open new terminal
python test.py
```
