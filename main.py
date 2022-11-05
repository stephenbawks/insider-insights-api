"""
API
"""

from functools import lru_cache
from loguru import logger
import httpx
import json
import os
import pathlib

from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import List, Optional, Union

from fastapi import FastAPI, status, Response, HTTPException


finance_api_key = os.environ.get("finance_api_api_key")

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



def query_yahoo_quote_summary(ticker_symbol: str) -> Union[dict, None]:
    """
    Query the Yahoo Financial API to pull back financial details for a single ticker symbol

    Args:
        ticker_symbol (str): The ticker symbol to pull information about.
    Returns:
        dict: The financial data for the ticker
    """

    url = f"https://yfapi.net/v11/finance/quoteSummary/{ticker_symbol}"

    headers = {
        "X-API-KEY": finance_api_key,
        "accept": "application/json"
    }

    query_string = {"modules":"defaultKeyStatistics,assetProfile,summaryDetail,financialData,price,earnings,earningsHistory"}

    response = httpx.get(url, headers=headers, params=query_string)
    response_json = json.loads(response.text)

    if response_json.get("quoteSummary").get("result") is None:
        print(response_json)
        return None

    return response_json


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


@app.get("/ticker/{ticker_symbol}", status_code=200)
async def read_item(ticker_symbol):

    ticker_upper = ticker_symbol.upper()

    yahoo_ticker_response = query_yahoo_quote_summary(ticker_symbol=ticker_upper)
    if yahoo_ticker_response is None:
        missing_ticker = {
            "ticker": ticker_upper,
            "error": "Cannot find ticker"
        }
        return Response(status_code=404, media_type="application/json", content=json.dumps(missing_ticker))

    ticker_details = yahoo_ticker_response.get("quoteSummary").get("result")[0]
    asset_profile = ticker_details.get("assetProfile") or {"assetProfile": {}}
    financial_details = ticker_details.get("financialData") or {"financialData": {}}
    default_stats = ticker_details.get("defaultKeyStatistics") or {"defaultKeyStatistics": {}}
    summary_detail = ticker_details.get("summaryDetail") or {"summaryDetail": {}}
    price_detail = ticker_details.get("price") or {"price": {}}

    body = {
        "ticker": ticker_upper,
        "shortName": price_detail.get("shortName") or None,
        "industry": asset_profile.get("industry") or None,
        "sector": asset_profile.get("sector") or None,
        "address1": asset_profile.get("address1") or None,
        "city": asset_profile.get("city") or None,
        "state": asset_profile.get("state") or None,
        "zipCode": asset_profile.get("zip") or None,
        "country": asset_profile.get("country") or None,
        "phone": asset_profile.get("phone") or None,
        "website": asset_profile.get("website") or None,
        "fiftyTwoWeekHigh": summary_detail.get("fiftyTwoWeekHigh").get("raw") or None,
        "fiftyTwoWeekLow": summary_detail.get("fiftyTwoWeekLow").get("raw") or None,
        "averageDailyVolume10Day": divide_by_1000(value=price_detail.get("averageDailyVolume10Day", {"averageDailyVolume10Day": {}}).get("raw")) or None,
        "averageDailyVolume3Month": divide_by_1000(value=price_detail.get("averageDailyVolume3Month", {"averageDailyVolume3Month": {}}).get("raw")) or None,
        "marketCap": divide_by_1000000(value=summary_detail.get("marketCap", {"marketCap": {}}).get("raw")) or None,
        "forwardPE":summary_detail.get("forwardPE", {"forwardPE": {}}).get("raw") or None,
        "trailingPE": summary_detail.get("trailingPE", {"trailingPE": {}}).get("raw") or None,
        "fullExchangeName":price_detail.get("exchangeName") or None,
        "currentPrice": summary_detail.get("previousClose", {"previousClose": {}}).get("raw") or None,
        "totalCashPerShare": financial_details.get("totalCashPerShare", {"totalCashPerShare": {}}).get("raw") or None,
        "operatingMargins": multiply_by_100(financial_details.get("operatingMargins", {"operatingMargins": {}}).get("raw")) or None,
        "freeCashflow": divide_by_1000000(value=financial_details.get("freeCashflow", {"freeCashflow": {}}).get("raw")) or None,
        "grossMargins": multiply_by_100(value=financial_details.get("grossMargins", {"grossMargins": {}}).get("raw")) or None,
        "ebitda": divide_by_1000000(value=financial_details.get("ebitda", {"ebitda": {}}).get("raw")) or None,
        "totalDebt": divide_by_1000000(value=financial_details.get("totalDebt", {"totalDebt": {}}).get("raw")) or None,
        "debtToEquity":financial_details.get("debtToEquity", {"debtToEquity": {}}).get("raw") or None,
        "currentRatio": financial_details.get("currentRatio", {"currentRatio": {}}).get("raw") or None,
        "totalRevenue": divide_by_1000000(value=financial_details.get("totalRevenue", {"totalRevenue": {}}).get("raw")) or None,
        "profitMargins": multiply_by_100(value=financial_details.get("profitMargins", {"profitMargins": {}}).get("raw")) or None,
        "targetHighPrice":financial_details.get("targetHighPrice", {"targetHighPrice": {}}).get("raw") or None,
        "targetLowPrice": financial_details.get("targetLowPrice", {"targetLowPrice": {}}).get("raw") or None,
        "targetMeanPrice": financial_details.get("targetMeanPrice", {"targetMeanPrice": {}}).get("raw") or None,
        "targetMedianPrice": financial_details.get("targetMedianPrice", {"targetMedianPrice": {}}).get("raw") or None,
        "recommendationMean": financial_details.get("recommendationMean", {"recommendationMean": {}}).get("raw") or None,
        "recommendationKey": financial_details.get("recommendationKey") or None,
        "numberOfAnalystOpinions": financial_details.get("numberOfAnalystOpinions", {"numberOfAnalystOpinions": {}}).get("raw") or None,
        "returnOnAssets": financial_details.get("returnOnAssets", {"returnOnAssets": {}}).get("raw") or None,
        "operatingCashflow": financial_details.get("operatingCashflow", {"operatingCashflow": {}}).get("raw") or None,
        "earningsGrowth": multiply_by_100(value=financial_details.get("earningsGrowth", {"earningsGrowth": {}}).get("raw")) or None,
        "revenueGrowth": multiply_by_100(value=financial_details.get("revenueGrowth", {"revenueGrowth": {}}).get("raw")) or None,
        "ebitdaMargins": divide_by_1000000(value=financial_details.get("ebitdaMargins", {"ebitdaMargins": {}}).get("raw")) or None,
        "fiftytwoWeekChange":default_stats.get("52WeekChange", {"52WeekChange": {}}).get("raw") or None,
        "floatShares": divide_by_1000000(value=default_stats.get("floatShares", {"floatShares": {}}).get("raw")) or None,
        "priceToBook": default_stats.get("priceToBook", {"priceToBook": {}}).get("raw") or None,
        "sharesShort": divide_by_1000000(value=default_stats.get("sharesShort", {"sharesShort": {}}).get("raw")) or None,
        "shortRatio": default_stats.get("shortRatio", {"shortRatio": {}}).get("raw") or None,
        "shortPercentOfFloat": multiply_by_100(value=default_stats.get("shortPercentOfFloat", {"shortPercentOfFloat": {}}).get("raw")) or None,
        "heldPercentInsiders": multiply_by_100(value=default_stats.get("heldPercentInsiders", {"heldPercentInsiders": {}}).get("raw")) or None,
        "heldPercentInstitutions": multiply_by_100(value=default_stats.get("heldPercentInstitutions", {"heldPercentInstitutions": {}}).get("raw")) or None,
        "lastFiscalYearEnd": default_stats.get("lastFiscalYearEnd", {"lastFiscalYearEnd": {}}).get("fmt") or None,
        "forwardEps": default_stats.get("forwardEps", {"forwardEps": {}}).get("raw") or None,
        "enterpriseToEbitda": default_stats.get("enterpriseToEbitda", {"enterpriseToEbitda": {}}).get("raw") or None,
        "enterpriseToRevenue": default_stats.get("enterpriseToRevenue", {"enterpriseToRevenue": {}}).get("raw") or None,
        "trailingEps": default_stats.get("trailingEps", {"trailingEps": {}}).get("raw") or None,
        "lastSplitDate": default_stats.get("lastSplitDate", {"lastSplitDate": {}}).get("fmt") or None,
        "lastSplitFactor": default_stats.get("lastSplitFactor") or None,
        "sharesShortPriorMonth": divide_by_1000000(value=default_stats.get("sharesShortPriorMonth", {"sharesShortPriorMonth": {}}).get("raw")) or None,
        "enterpriseValue": default_stats.get("enterpriseValue", {"enterpriseValue": {}}).get("raw") or None,
        "earningsQuarterlyGrowth": multiply_by_100(value=default_stats.get("earningsQuarterlyGrowth", {"earningsQuarterlyGrowth": {}}).get("raw")) or None,
        "revenueQuarterlyGrowth": multiply_by_100(value=default_stats.get("revenueQuarterlyGrowth", {"revenueQuarterlyGrowth": {}}).get("raw")) or None,
        "mostRecentQuarter": default_stats.get("mostRecentQuarter", {"mostRecentQuarter": {}}).get("fmt") or None,
        "pegRatio": default_stats.get("pegRatio", {"pegRatio": {}}).get("raw") or None,
        "beta": summary_detail.get("beta", {"beta": {}}).get("raw") or None,
        "priceToSalesTrailing12Months": summary_detail.get("priceToSalesTrailing12Months", {"priceToSalesTrailing12Months": {}}).get("raw") or None,
        "dividendYield": multiply_by_100(value=summary_detail.get("dividendYield", {"dividendYield": {}}).get("raw")) or None
    }

    return Response(status_code=200, media_type="application/json", content=json.dumps(body))

@app.get("/", status_code=200)
async def root():
    """
    Main

    """
    return {"message": "Hello World!!!!!!!!!!!!!!!!"}
