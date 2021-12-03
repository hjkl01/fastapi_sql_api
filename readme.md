### 直接部署

```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
pip install -r ./requirements.txt
# update .env
uvicorn main:app

# open new terminal
python test.py
```

### with docker-compose
```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
# update .env and config/redis.conf
mkdir -p data/redis
docker-compose up -d
```
