### 概述
  本项目可通过http请求管理redis队列，对mongo的数据insert和query。
  对爬虫来讲，保存数据时，网络请求消耗的时间是可接受的。
  避免了重复配置redis和mongo。

### 直接部署

```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
pip install -r ./requirements.txt
# update .secrets.toml
uvicorn main:app --workers=8

# open new terminal
python example.py
```

### with docker-compose
```sh
git clone https://github.com/lesssound/fastapi_redis
cd fastapi_redis 
# update .secrets.toml and config/redis.conf
mkdir -p data/redis
docker-compose up -d
```
