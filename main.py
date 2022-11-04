from fastapi import FastAPI, status, Response, HTTPException
import pathlib
from functools import lru_cache
import json
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import List, Optional, Union


app = FastAPI()





@lru_cache()
def get_holiday_dates() -> List[dict]:
    """
    Opens a file that has officially listed holidays that the market is closed for

    Returns:
        List[dict]: List of holidays
    """

    file_contents = pathlib.Path("holidays.txt").read_text()
    return json.loads(file_contents)


@lru_cache()
@app.get("/holidays", status_code=200, content_type="application/json")
async def is_holiday():
    return pathlib.Path("holidays.txt").read_text()


@app.get("/", status_code=200)
async def root():
    return {"message": "Hello World"}
