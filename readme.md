### 直接部署

```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
pip install -r ./requirements.txt
# update .secrets.toml
uvicorn main:app --workers=8

# open new terminal
python test.py
```

### with docker-compose
```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
# update .secrets.toml and config/redis.conf
mkdir -p data/redis
docker-compose up -d
```
