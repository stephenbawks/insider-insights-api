from datetime import date, datetime, timedelta
from typing import List, Optional, Union

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
