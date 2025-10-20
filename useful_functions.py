import requests
from datetime import datetime, timezone
from requests import RequestException, HTTPError
import custom_exceptions
from dotenv import load_dotenv
from pathlib import Path
import os
from cachetools import cached, TTLCache

# loading the enviormental variables
DOTENV_PATH = Path(__file__).parent / ".env"
load_dotenv(str(DOTENV_PATH))

# External APIs will use
FRANKFURTER_API_BASE_URL = "https://api.frankfurter.dev"
BRAPI_API_BASE_URL = "https://brapi.dev/api"

# Establishing our http session to send requests
session = requests.Session()


def get_api_basic_info() -> dict:
    return {
        "APIName": "Finance API",
        "description": "A simple API to get real-time and historical currency quotes, as well as stock "
                        +"information from the Brazilian stock exchange (B3)",
        "author": "Gustavo Henrique de Oliveira Dias",
        "contact": {
            "github": "https://github.com/GustavoDiaso",
            "linkedin": "https://www.linkedin.com/in/gustavodiaso",
        },
        "externalAPISUsed": {
            "FrankFurter API": "https://frankfurter.dev/",
            "Brapi API": "https://brapi.dev/",
        },
        "serverTimeUTC": datetime.now(timezone.utc).isoformat(),
        "gettingStarted": {
            "exampleEndpoints": [
                "/v1/currencies",
                "/v1/conversion/historical?from=USD&to=BRL&amount=1",
                "/v1/conversion/historical?from=USD&to=BRL&amount=1&date=2025-10-12",
                "/v1/conversion/interval?from=USD&to=BRL&start_date=2025-01-09&end_date=2025-02-09",
                "/v1/b3stocks/all",
                "/v1/b3stocks/quote?ticker=PETR3&range=5d&interval=1d",
                "/v1/b3stocks/stocksinfo?sector=Retail+Trade&limit=10&sortedBy=volume",
            ]
        },
    }


def get_existing_currencies() -> dict:
    return {
        "AUD": "Australian Dollar",
        "BGN": "Bulgarian Lev",
        "BRL": "Brazilian Real",
        "CAD": "Canadian Dollar",
        "CHF": "Swiss Franc",
        "CNY": "Chinese Renminbi Yuan",
        "CZK": "Czech Koruna",
        "DKK": "Danish Krone",
        "EUR": "Euro",
        "GBP": "British Pound",
        "HKD": "Hong Kong Dollar",
        "HUF": "Hungarian Forint",
        "IDR": "Indonesian Rupiah",
        "ILS": "Israeli New Sheqel",
        "INR": "Indian Rupee",
        "ISK": "Icelandic Króna",
        "JPY": "Japanese Yen",
        "KRW": "South Korean Won",
        "MXN": "Mexican Peso",
        "MYR": "Malaysian Ringgit",
        "NOK": "Norwegian Krone",
        "NZD": "New Zealand Dollar",
        "PHP": "Philippine Peso",
        "PLN": "Polish Złoty",
        "RON": "Romanian Leu",
        "SEK": "Swedish Krona",
        "SGD": "Singapore Dollar",
        "THB": "Thai Baht",
        "TRY": "Turkish Lira",
        "USD": "United States Dollar",
        "ZAR": "South African Rand",
    }


def currency_exists(currency: str) -> bool:
    """Verifies if the given currency exists"""
    currencies = get_existing_currencies()
    return True if currency in currencies.keys() else False


def date_is_real(str_date: str) -> bool:
    """Checks if a given date in string format is equivalent to a real date"""
    date_formats = ["%Y-%m-%d", "%d-%m-%Y"]
    for date_format in date_formats:
        try:
            datetime.strptime(str_date, date_format)
            return True
        except ValueError:
            continue

    return False


def get_formatted_date(str_date: str) -> str:
    """This function converts a given date in string format to the following pattern: %Y-%m-%d, and returns it"""
    if not date_is_real(str_date):
        raise custom_exceptions.NonExistentDateError(
            f"The following date does not exist: {str_date}"
        )

    try:
        formatted_date = datetime.strptime(str_date, "%Y-%m-%d")
    except ValueError:
        formatted_date = datetime.strptime(str_date, "%d-%m-%Y")

    return formatted_date.date().isoformat()


def consume_frankfurter_api(
    endpoint: str, params: dict | None = None, http_session: requests.Session = session
) -> dict | None:

    clean_endpoint = endpoint.lstrip("/")

    url = f"{FRANKFURTER_API_BASE_URL}/{clean_endpoint}"

    # Consuming the API
    response = http_session.get(url, params=params, timeout=10)

    # automatically raises an exception if the HTTPS request returned an unsuccessful status code
    response.raise_for_status()

    return response.json()


def validate_historical_endpoint_params(request) -> dict:
    """
    This function validates the URL parameters passed in the request to the historical endpoin and returns them
    pre-formatted so they can be processed. If any passed parameter doesn't match what was expected,
    the function raises an error.
    """
    from_currency = request.args.get("from") or "USD"
    to_currencies = request.args.get("to")
    amount = request.args.get("amount") or "1"
    date = request.args.get("date") or datetime.now().date().isoformat()

    # --Validating the parameters-- #
    if not currency_exists(from_currency):
        raise custom_exceptions.BadRequestError(
            f"The following currency is not supported: {from_currency}"
        )

    if to_currencies is not None:
        for currency in to_currencies.split(","):
            if not currency_exists(currency):
                raise custom_exceptions.BadRequestError(
                    f"The following currency is not supported: {currency}"
                )

    try:
        int(amount)
    except:
        raise custom_exceptions.BadRequestError(
            f"The 'amount' parameter must be a number"
        )

    try:
        date = get_formatted_date(date)
    except custom_exceptions.NonExistentDateError as err:
        raise custom_exceptions.BadRequestError(str(err))

    # -- Returning the URL parameters already validated and in the desired formatting -- #
    return {
        "from_currency": from_currency,
        "to_currencies": to_currencies,
        "amount": amount,
        "date": date,
    }


def validate_interval_endpoint_params(request) -> dict:
    """
    This function validates the URL parameters passed in the request to the interval endpoin and returns them
    pre-formatted so they can be processed. If any passed parameter doesn't match what was expected,
    the function raises an error.
    """
    from_currency = request.args.get("from") or "USD"
    to_currencies = request.args.get("to")
    amount = request.args.get("amount") or "1"
    start_date = request.args.get("start_date") or datetime.now().date().isoformat()
    end_date = request.args.get("end_date") or datetime.now().date().isoformat()

    # --Validating the parameters-- #
    if not currency_exists(from_currency):
        raise custom_exceptions.BadRequestError(
            f"The following currency does not exist: {from_currency}"
        )

    if to_currencies is not None:
        for currency in to_currencies.split(","):
            if not currency_exists(currency):
                raise custom_exceptions.BadRequestError(
                    f"The following currency does not exist: {currency}"
                )

    try:
        int(amount)
    except:
        raise custom_exceptions.BadRequestError(
            f"The 'amount' parameter must be a number"
        )

    try:
        start_date = get_formatted_date(start_date)
        end_date = get_formatted_date(end_date)
    except custom_exceptions.NonExistentDateError as err:
        raise custom_exceptions.BadRequestError(str(err))

    # -- Returning the URL parameters already validated and in the desired formatting -- #
    return {
        "from_currency": from_currency,
        "to_currencies": to_currencies,
        "amount": amount,
        "start_date": start_date,
        "end_date": end_date,
    }


def get_b3_avaliable_market_sectors() -> set:
    """This function returns all market sectors of stocks traded on B3"""
    return {
        "Retail Trade",
        "Energy Minerals",
        "Health Services",
        "Utilities",
        "Finance",
        "Consumer Services",
        "Consumer Non-Durables",
        "Non-Energy Minerals",
        "Commercial Services",
        "Distribution Services",
        "Transportation",
        "Technology Services",
        "Process Industries",
        "Communications",
        "Producer Manufacturing",
        "Miscellaneous",
        "Electronic Technology",
        "Industrial Services",
        "Health Technology",
        "Consumer Durables",
    }


def validate_brapi_api_key_declaration() -> None:
    """This function validates the existence of the BRAPI API KEY in the enviromental variables"""
    if "BRAPI_API_KEY" not in os.environ or not os.environ["BRAPI_API_KEY"]:
        raise custom_exceptions.MissingBrapiAPIKeyError(
            '\nThe "BRAPI_API_KEY" environment variable is missing. \n'
            + 'Please, create a ".env" file in the root directory of the project and add your BRAPI API key as follows: \n'
            + "BRAPI_API_KEY=your_api_key_here \n"
            + "You can get a free API key by creating an account at https://brapi.dev/\n"
        )


def consume_brapi_api(
    endpoint: str, params: dict | None = None, http_session: requests.Session = session
) -> dict | None:

    validate_brapi_api_key_declaration()

    # Just making sure the first char in the endpoint str is a /
    clean_endpoint = endpoint.lstrip("/")

    url = f"{BRAPI_API_BASE_URL}/{clean_endpoint}"

    try:
        # Consuming the API
        response = http_session.get(
            url=url,
            params=params,
            timeout=10,
            headers={"Authorization": f"Bearer {os.environ['BRAPI_API_KEY']}"},
        )
        # raises an exception if the HTTPS request returned an unsuccessful status code
        response.raise_for_status()

    except HTTPError as err:
        # If the error was due to our API key being invalid, then we raise a specific error
        if err.response.status_code == 401:
            raise custom_exceptions.InvalidBrapiAPIKeyError(
                "The provided BRAPI API key is invalid. Please, check the key and try again."
            )
        else:
            raise

    return response.json()


@cached(TTLCache(maxsize=1, ttl=10800))
def get_b3_traded_stocks():
    """This function returns the tickers of all stocks traded on B3 at the present time"""
    # Requesting the tickers to brapi API
    response = consume_brapi_api(endpoint="/available")
    return set(response["stocks"])


def validate_quotes_endpoint_params(request) -> dict:
    """
    This function validates the URL parameters passed in the request to the quote endpoin and returns them
    pre-formatted so they can be processed. If any passed parameter doesn't match what was expected,
    the function raises an error.
    """
    ticker = request.args.get("ticker")
    analysis_time_range = request.args.get("range") or "1d"
    interval_between_quotations = request.args.get("interval") or "1d"

    # This parameter tells whether users want to include basic fundamental data such as  PE (Price-to-Earnings ratio)
    # and EPS (Earnings Per Share) in the response
    fundamental_data = request.args.get("fundamental")

    # This parameter tells whether users want to include information about dividends and interest
    # on equity historically paid by the asset in the response.
    dividends = request.args.get("dividends")

    # -- Verifications --#
    if not ticker:
        raise custom_exceptions.BadRequestError(
            "At least one stock ticker must be specified. Exemples: PETR3, GOLL54"
        )
    else:
        try:
            if ticker not in get_b3_traded_stocks():
                raise custom_exceptions.BadRequestError(
                    f"The ticker '{ticker}' is not traded on B3"
                )
        # If we could not get the up-to-date list of stocks traded on B3, then we just skip this verification
        # and let the brapi API handle the invalid ticker error
        except RequestException:
            pass

    if fundamental_data and fundamental_data not in ["true", "false"]:
        raise custom_exceptions.BadRequestError(
            "The 'fundamental' parameter only accepts 'true' or 'false' as a value"
        )

    if dividends and dividends not in ["true", "false"]:
        raise custom_exceptions.BadRequestError(
            "The 'dividens' parameter only accepts 'true' or 'false' as a value"
        )

    # -- If all verifications passed, then return a dictionary containing the URL parameters formatted and ready to use

    return {
        "ticker": ticker,
        "analysis_time_range": analysis_time_range,
        "interval_between_quotations": interval_between_quotations,
        "fundamental_data": fundamental_data,
        "dividends": dividends,
    }


def validate_stocksinfo_endpoint_params(request) -> dict:
    """
    This function validates the URL parameters passed in the request to the stocksinfo endpoin and returns them
    pre-formatted so they can be processed. If any passed parameter doesn't match what was expected,
    the function raises an error.
    """

    # stock market sector
    sector = request.args.get("sector")

    # 'sorted_by' determines the field by which the stocks will be sorted
    sorted_by = request.args.get("sortedBy") or "name"

    # 'order' determines the order in which the sorted stocks will appear in the response.
    # Smallest to largest, bottom to top : asc
    # largest to smallest, top to bottom: desc
    order = request.args.get("order") or "asc"

    # limits the number of stocks that will be shown in the response at a time
    limit = request.args.get("limit")

    # Page number of results to be returned, considering the specified limit. Starts at 1.
    # Ex: limit=2 sortedBy=name. Page 1: AAA, AAB . Page 2: AAC AAD
    page = request.args.get("page")

    # -- Verifications -- #

    if sector:
        available_market_sectors = get_b3_avaliable_market_sectors()

        if sector not in available_market_sectors:
            raise custom_exceptions.BadRequestError(
                f"The sector '{sector}' does not include any group of shares traded on b3.\n"
                + f"Available market sectors are: \n"
                + " | ".join(available_market_sectors)
            )

    if sorted_by:
        valid_sort_options = [
            "name",
            "close",
            "change",
            "change_abs",
            "volume",
            "market_cap_basic",
            "sector",
        ]

        if sorted_by not in valid_sort_options:
            raise custom_exceptions.BadRequestError(
                "The parameter sortedBy only accepts the following options: "
                + " | ".join(valid_sort_options)
            )

    if order and order not in ["asc", "desc"]:
        raise custom_exceptions.BadRequestError(
            "The 'order' parameter can only receive 'asc' or 'desc'"
        )

    if page:
        try:
            if int(page) < 1:
                raise custom_exceptions.BadRequestError(
                    "The 'page' parameter must be a number greater than or equal to 1"
                )
        except ValueError:
            raise custom_exceptions.BadRequestError(
                f"The 'page' parameter must be a number"
            )

    if limit:
        try:
            if int(limit) < 1:
                raise custom_exceptions.BadRequestError(
                    "The 'limit' parameter must be a number greater than or equal to 1"
                )
        except ValueError:
            raise custom_exceptions.BadRequestError(
                f"The 'limit' parameter must be a number"
            )

    return {
        "sector": sector,
        "sortedBy": sorted_by,
        "order": order,
        "page": page,
        "limit": limit,
    }


if __name__ == "__main__":
    print(os.environ["BRAPI_API_KEY"])
