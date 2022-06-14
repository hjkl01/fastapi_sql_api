# -*- coding: UTF-8 -*-
'''
@Project ：work 
@File ：html_api.py
@IDE  ：PyCharm 
@Author ：Sun Li
@Date ：2022/6/13 15:08 
'''

import json
from datetime import datetime
import zlib
import os
from pydantic import BaseModel
from settings import Config, logger
from .user_api import get_current_username



class htmlItem(BaseModel):
    name: str = "test"
    date: str = datetime.now().strftime("%Y%m%d")
    filename: str = "test"
    cont: str = ""
    limit: int = 20

class htmlapi:
    def __init__(self):
        self.path = Config.HTML_HOST
    def html_if_exist(self, name, date):
        path = self.path + rf'\{name}' + rf'\{date}'
        if not os.path.exists(path):
            os.makedirs(path)
        return
    def html_zlib(self, cont):
        z = zlib.compress(cont.encode())
        res = zlib.decompress(z).decode()
        return res
    # async def html_insert(self, item: htmlItem, username: str = Depends(get_current_username)) -> dict:
    async def html_insert(self, item: htmlItem) -> dict:
        logger.info(item)
        self.html_if_exist(item.name, item.date)
        content = self.html_zlib(item.cont)
        filepath = self.path + rf'\{item.name}' + rf'\{item.date}' + rf'\{item.filename}.html'
        try:
            with open(filepath, 'wb') as f:
                f.write(content.encode())
            result = "save success"
            logger.info(result)
        except Exception as err:
                logger.err(err)
                result = err
        return {
            "success": "OK" if result == "save success" else "NG",
            "result": result,
            "created_at": datetime.now(),
        }
    async def html_query(self, item: htmlItem) -> dict:
        res = []
        logger.info(item)
        target_path = self.path + rf'\{item.name}' + rf'\{item.date}'
        if item.limit > 20 or item.limit is None or item.limit is False or item.limit == 0:
            _limit = 20
        else:
            _limit = item.limit
        try:
            all_files = os.listdir(target_path)

            for i in range(item.skip*_limit, len(all_files)):
            # f = open("GP.html", "r", encoding='utf-8')
            # html = f.read()
        except Exception as err:
            logger.err(err)
        return res
