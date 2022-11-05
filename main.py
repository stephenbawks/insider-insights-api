"""
API
"""

import pathlib
import json
from functools import lru_cache

from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import List, Optional, Union

from fastapi import FastAPI, status, Response, HTTPException




app = FastAPI()

def multiply_by_100(value: float) -> Union[float, None]:
    """
    Multiply a value by 100

    Args:
        value (float): The value to multiply by 100

    Returns:
        float: The value multiplied by 100 or None if the value is None

    """

    try:
        return value * 100
    except TypeError:
        return None


def divide_by_1000(value: float) -> Union[float, None]:
    """
    Multiply a value by 1000

    Args:
        value (float): The value to multiply by 1000

    Returns:
        float: The value divded by 1000 or None if the value is None

    """

    try:
        return value / 1000
    except TypeError:
        return None


def divide_by_1000000(value: float) -> Union[float, None]:
    """
    Multiply a value by 1000000

    Args:
        value (float): The value to multiply by 1000000

    Returns:
        float: The value divded by 1000000 or None if the value is None

    """

    try:
        return value / 1000000
    except TypeError:
        return None

def convert_datetime(dict_object: dict) -> dict:
    """
    Converts datetime objects to strings

    Args:
        dict_object (dict): Dictionary object to convert

    Returns:
        dict: _description_
    """
    for key in dict_object:
        if isinstance(dict_object[key], (datetime, date)):
            dict_object[key] = dict_object[key].strftime("%Y-%m-%d")
    return dict_object



# def query_yahoo_quote_summary(ticker_symbol: str) -> Union[dict, None]:
#     """
#     Query the Yahoo Financial API to pull back financial details for a single ticker symbol

#     Args:
#         ticker_symbol (str): The ticker symbol to pull information about.
#     Returns:
#         dict: The financial data for the ticker
#     """

#     url = f"https://yfapi.net/v11/finance/quoteSummary/{ticker_symbol}"

#     headers = {
#         "X-API-KEY": finance_api_key,
#         "accept": "application/json"
#     }

#     query_string = {"modules":"defaultKeyStatistics,assetProfile,summaryDetail,financialData,price,earnings,earningsHistory"}

#     response = http.request('GET', url, headers=headers, fields=query_string)
#     print(f"Response Status Code: {response.status}")

#     print(response.data.decode('utf-8'))
#     response_decoded = json.loads(response.data.decode('utf-8'))

#     if response_decoded.get("quoteSummary").get("result") is None:
#         print(response_decoded)
#         return None

#     return response_decoded


@lru_cache()
def get_holiday_dates() -> List[dict]:
    """
    Opens a file that has officially listed holidays that the market is closed for

    Returns:
        List[dict]: List of holidays
    """

    file_contents = pathlib.Path("holidays.txt").read_text()
    return json.loads(file_contents)


@app.get("/holidays", status_code=200)
async def is_holiday():
    """
    Get the list of holidays

    Returns:
        _type_: _description_
    """
    return pathlib.Path("holidays.txt").read_text()


# @app.get("/ticker/{ticker_symbol}", status_code=200)
# async def read_item(ticker_symbol):

#     ticker_upper = ticker_symbol.upper()

#     yahoo_ticker_response = query_yahoo_quote_summary(ticker_symbol=ticker_upper)
#     if yahoo_ticker_response is None:
#         raise HTTPException(status_code=404, detail=body)

#         body = {
#             "ticker": ticker_upper,
#             "error": "Cannot find ticker"
#         }

#     return json.dumps(body)

@app.get("/", status_code=200)
async def root():
    """
    Main

    """
    return {"message": "Hello World!!!!!!!!!!!!!!!!"}
