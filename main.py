# pylint: disable=import-error,invalid-name,line-too-long

"""
API
"""

from functools import lru_cache
from loguru import logger
# from data.database import SupabaseDB

import httpx
import json
import os
import pathlib
import pymysql.cursors

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras

from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import List, Optional, Union

from fastapi import FastAPI, status, Request, Response, HTTPException


# insider-insights-user
# a69izEWHHK2qTu4LCLz4hg
finance_api_key = os.environ.get("finance_api_api_key")


# conn = psycopg2.connect(
#     host = 'free-tier14.aws-us-east-1.cockroachlabs.cloud',
#     port = 26257,
#     user = 'insider-insights-user',
#     password = 'a69izEWHHK2qTu4LCLz4hg',
#     sslrootcert = '/root.crt',
#     database = 'historical_data',
#     options = '--cluster=upset-drake-6457'
# )

# cursor = conn.cursor()
# create_table = "CREATE TABLE IF NOT EXISTS ticker_data (id serial, ticker text, shortname text, PRIMARY KEY( id ));"
# drop_table = "DROP TABLE ticker_data;"
# cursor.execute(create_table)
# cursor.execute("CREATE TABLE IF NOT EXISTS \"ticker_data\" (\"id\" serial,\"ticker\" text,\"shortname\" text,PRIMARY KEY( id ));")
# cursor.execute("SELECT *;")

# with conn.cursor() as cursor:
#     get_sec_id = f"select id, ticker, shortName FROM ticker_data;"
#     cursor.execute(get_sec_id)
#     result = cursor.fetchone()
#     if result is None:
#         return None





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


def write_to_db(data: dict) -> None:
    """
    Write data to the database

    Args:
        data (dict): Data to write to the database
    """

    conn = psycopg2.connect(
        host = 'free-tier14.aws-us-east-1.cockroachlabs.cloud',
        port = 26257,
        user = 'insider-insights-user',
        password = 'a69izEWHHK2qTu4LCLz4hg',
        sslrootcert = '/root.crt',
        database = 'historical_data',
        options = '--cluster=upset-drake-6457'
    )

    ticker = data.get("ticker")
    shortname = data.get("shortName")

    with conn.cursor() as cursor:
        get_sec_id = f'INSERT INTO ticker_data (ticker, shortName) VALUES ("{ticker}", "{shortname}"));'
        cursor.execute(get_sec_id)


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
        missing_ticker = {
            "ticker": ticker_symbol,
            "error": "Cannot find ticker"
        }
        return Response(status_code=404, media_type="application/json", content=json.dumps(missing_ticker))

    return response_json


@lru_cache()
@app.get("/holidays", status_code=200)
async def is_holiday() -> List[dict]:
    """
    Get the list of holidays that are stored in a text file

    Returns:
        List[dict]: List of holidays
    """
    holidays = pathlib.Path("holidays.txt").read_text()
    return Response(status_code=200, media_type="application/json", content=holidays)



@lru_cache()
def get_close_price_date(ticker_symbol: str, lookup_date: str) -> Union[float, None]:
    """
    Get the close price for a given date

    Args:
        sec_id (str): The SEC ID for the ticker symbol
        lookup_date (str): The date to lookup

    Returns:
        Union[float, None]: Close price for a given date or None if no data is found
    """

    onprem_historical = pymysql.connect(
        host="69.10.161.9",
        user="root",
        password="r@gn@r0k10",
        db="exofficio",
        cursorclass=pymysql.cursors.DictCursor,
    )

    with onprem_historical.cursor() as cursor:
        # find_starting_date = f"select last from historical where sec_id = '{sec_id}' and date = '{lookup_date}';"
        find_starting_date = f"select last from historical where ticker = '{ticker_symbol}' and date = '{lookup_date}';"
        cursor.execute(find_starting_date)
        result = cursor.fetchone()
        print(result)
        if result is None:
            return None

        close_price = result.get("last") or None
        print(f"Date: {lookup_date} - Close Price: {close_price}")

        return close_price

def calculate_change_percentage(start_close_price: str, lookup_date: str, ticker_symbol: str) -> Union[float, None]:
    """
    Calculate the percentage change between the start close price and the lookup date

    Args:
        start_close_price (str): Starting close price
        lookup_date (str): Date to lookup
        sec_id (str): SEC ID

    Returns:
        Union[float, None]: Average difference or None if no data is found
    """

    print(f"Starting Close Price: {start_close_price} - Lookup Date: {lookup_date} - SEC ID: {ticker_symbol}")

    onprem_historical = pymysql.connect(
        host="69.10.161.9",
        user="root",
        password="r@gn@r0k10",
        db="exofficio",
        cursorclass=pymysql.cursors.DictCursor,
    )

    with onprem_historical.cursor() as cursor:

        find_specific_date = f"select last from historical where ticker = '{ticker_symbol}' and date = '{lookup_date}';"
        cursor.execute(find_specific_date)
        result = cursor.fetchone()
        print(result)
        if result is None:
            return 0

        historical_close = result.get("last")
        print(f"Previous Date Close: {lookup_date} - Close Price: {historical_close}")

        return ((start_close_price / historical_close) - 1) * 100



@app.get("/percentchange/{ticker_symbol}/{start_date}")
def calculate_change_percentages(ticker_symbol: str, start_date: Optional[str] = None) -> dict:
    ticker_upper = ticker_symbol.upper()
    logger.info(f"Looking up ticker symbol {ticker_upper}")

    holidays = get_holiday_dates()

    # Check to see if the date is on a weekend day
    datetime_start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if datetime_start_date.weekday() > 4:
        # Date specific is on a weekend, return and error
        body = {
            "start_date": start_date,
            "message": "Date is on a weekend"
        }
        return Response(status_code=400, media_type="application/json", content=json.dumps(body))

    if start_date in holidays:
        # Date specific is on a holiday, return and error
        body = {
            "start_date": start_date,
            "message": "Date is on a holiday"
        }
        return Response(status_code=400, media_type="application/json", content=json.dumps(body))

    close_price = get_close_price_date(ticker_symbol=ticker_upper, lookup_date=start_date)
    if close_price is None:
        # Cannot find a close price for the date, return an error
        body = {
            "start_date": start_date,
            "error": "Cannot find a close price for the date"
        }
        return Response(status_code=404, media_type="application/json", content=json.dumps(body))

    four_weeks_ago = (datetime_start_date - timedelta(weeks=4)).strftime("%Y-%m-%d")
    thirteen_weeks_ago = (datetime_start_date - timedelta(weeks=13)).strftime("%Y-%m-%d")
    twenty_six_weeks_ago = (datetime_start_date - timedelta(weeks=26)).strftime("%Y-%m-%d")
    fifty_two_weeks_ago = (datetime_start_date - timedelta(weeks=52)).strftime("%Y-%m-%d")

    four_week_change = calculate_change_percentage(start_close_price=close_price, lookup_date=four_weeks_ago, ticker_symbol=ticker_upper)
    thirteen_week_change = calculate_change_percentage(start_close_price=close_price, lookup_date=thirteen_weeks_ago, ticker_symbol=ticker_upper)
    twenty_six_week_change = calculate_change_percentage(start_close_price=close_price, lookup_date=twenty_six_weeks_ago, ticker_symbol=ticker_upper)
    fifty_two_week_change = calculate_change_percentage(start_close_price=close_price, lookup_date=fifty_two_weeks_ago, ticker_symbol=ticker_upper)

    body = {
        "ticker": ticker_upper,
        "start_date": start_date,
        "4wk_change": four_week_change,
        "13wk_change": thirteen_week_change,
        "26wk_change": twenty_six_week_change,
        "52wk_change": fifty_two_week_change
    }
    return Response(status_code=200, media_type="application/json", content=json.dumps(body))


@app.get("/ticker/{ticker_symbol}", status_code=200)
async def read_item(ticker_symbol):

    ticker_upper = ticker_symbol.upper()

    yahoo_ticker_response = query_yahoo_quote_summary(ticker_symbol=ticker_upper)

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

    data = {"ticker":ticker_upper, "shortName": price_detail.get("shortName")}
    write_to_db(data)
    return Response(status_code=200, media_type="application/json", content=json.dumps(body))

@app.get("/", status_code=200)
async def root():
    """
    Main

    """
    return {"message": "Hello World!!!!!!!!!!!!!!!!"}
