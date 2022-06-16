# -*- coding: UTF-8 -*-
"""
@Project ：work 
@File ：html_api.py
@idE  ：PyCharm 
@Author ：Sun Li
@date ：2022/6/13 15:08 
"""

import os
import zlib
from datetime import datetime

from pydantic import BaseModel
from fastapi import Depends

from settings import Config, logger
from .user_api import get_current_username
from .mongo_api import MongoItem, MongoAPI


class htmlItem(BaseModel):
    db: str = "test"
    tablename: str = datetime.now().strftime("%Y%m%d")
    id: str
    text: str = ""
    limit: int = 20
    skip: int = 0


class HtmlAPI:
    def __init__(self):
        self.path = Config.HTML_PATH

    def html_zlib(self, text):
        z = zlib.compress(text.encode())
        res = zlib.decompress(z).decode()
        return res

    async def html_insert(self, item: htmlItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(item)

        # if path exists
        pre_path = f"{self.path}/{item.db.replace('/','')}/{item.tablename.replace('/','')}"
        if not os.path.exists(pre_path):
            os.makedirs(pre_path)

        # compress
        content = zlib.decompress(zlib.compress(item.text.encode())).decode()
        filepath = f"{pre_path}/{item.id.replace('/','')}"

        # save to path
        result = None
        try:
            with open(filepath, "w") as f:
                f.write(content)
            logger.info(result)
        except Exception as err:
            logger.error(err)
            result = err

        # save to mongo
        item = {
            "db": "html",
            "tablename": f"{item.db}_{item.tablename}",
            "values": {
                "_id": item.id,
                "path": f"{item.db.replace('/','')}/{item.tablename.replace('/','')}/{item.id.replace('/','')}",
            },
        }
        item = MongoItem(**item)
        logger.debug(item.dict())
        result = MongoAPI().insert_api(item)

        return {
            "success": "OK" if result is None else "NG",
            "result": result,
            "created_at": datetime.now(),
        }

    async def html_query(self, item: htmlItem, username: str = Depends(get_current_username)) -> dict:
        logger.info(item)
        target_path = f"{self.path}/{item.db.replace('/','')}/{item.tablename.replace('/','')}"

        if item.limit > 20 or item.limit is None or item.limit is False or item.limit == 0:
            _limit = 20
        else:
            _limit = item.limit

        result = []
        try:
            all_files = os.listdir(target_path)
            logger.debug(all_files)
            for i in range(item.skip * _limit, len(all_files)):
                logger.debug(i)
                d = {"id": all_files[i]}
                with open(f"{target_path}/{all_files[i]}", "r") as file:
                    d["text"] = file.read()
                result.append(d)
        except Exception as err:
            logger.error(err)

        return {
            "success": "OK" if result != [] else "NG",
            "result": result,
            "created_at": datetime.now(),
        }
