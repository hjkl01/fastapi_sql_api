import asyncio
from datetime import datetime

from pydantic import BaseModel
from fastapi import Depends
import pymysql
import records

from settings import Config, logger
from .user_api import get_current_username

pymysql.install_as_MySQLdb()


class MySQLItem(BaseModel):
    db: str = "test"
    query: str


async def mysql_api(
    item: MySQLItem, username: str = Depends(get_current_username)
) -> dict:
    logger.info(item)
    try:
        result = None
        db = records.Database(f"{Config.MYSQL_URI}/{item.db}")
        rows = db.query(item.query)
        logger.debug(rows.all())
        result = rows.export("json")
        db.close()
    except Exception as err:
        logger.error(err)

    return {
        "success": "OK",
        "result": result,
        "created_at": datetime.now(),
    }
