from fastapi import FastAPI
import pathlib
from functools import lru_cache
import json
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import List, Optional, Union


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
