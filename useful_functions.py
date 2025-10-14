import requests
from datetime import datetime, timezone
import custom_exceptions
from dotenv import load_dotenv
from pathlib import Path
import os

#loading the enviormental variables
DOTENV_PATH = Path(__file__).parent / '.env'
load_dotenv(str(DOTENV_PATH))

# External APIs will use
FRANKFURTER_API_BASE_URL = "https://api.frankfurter.dev"
BRAPI_API_BASE_URL = "https://brapi.dev/api"

# Establishing our http session to send requests
session = requests.Session()


def consume_frankfurter_api(
    endpoint: str, params: dict = None, http_session: requests.Session = session
) -> dict | None:
    # Just making sure the first char in the endpoint str is a /
    if endpoint[0] != "/":
        endpoint = "/" + endpoint

    url = f"{FRANKFURTER_API_BASE_URL}{endpoint}"

    # Consuming the API
    response = http_session.get(url, params=params, timeout=10)

    # automatically raises an exception if the HTTPS request returned an unsuccessful status code
    response.raise_for_status()

    return response.json()


def get_api_basic_info() -> dict:
     return {
        "api_name": "Currency API",
        "description": "A simple API to get real-time and historical currency quotes.",
        "author": "Gustavo Henrique de Oliveira Dias",
        "contact": {
            "github": "https://github.com/GustavoDiaso",
            "linkedin": "https://www.linkedin.com/in/gustavodiaso",
        },
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "getting_started": {
            "example_endpoints": [
                "/v1/currencies",
                "/v1/historical?from=USD&to=BRL&amount=1",
                "/v1/historical?from=USD&to=BRL&amount=1&date=2025-10-12",
                "/v1/interval?from=USD&to=BRL&start_date=2025-01-09&end_date=2025-02-09"
            ]
        }
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
    date_formats = ["%Y-%m-%d", "%d-%m-%Y"]
    for date_format in date_formats:
        try:
            datetime.strptime(str_date, date_format)
            return True
        except ValueError:
            continue

    return False


def get_formatted_date(str_date: str) -> str:
    if not date_is_real(str_date):
        raise custom_exceptions.NonExistentDateError(f"The following date does not exist: {str_date}")

    try:
        formatted_date = datetime.strptime(str_date, "%Y-%m-%d")
    except ValueError:
        formatted_date = datetime.strptime(str_date, "%d-%m-%Y")

    return formatted_date.date().isoformat()


def validate_historical_endpoint_params(request):

    from_currency = request.args.get("from") or 'USD'
    to_currencies = request.args.get("to")
    amount = request.args.get("amount") or '1'
    date = request.args.get("date") or datetime.now().isoformat()

    # --Validating the parameters-- #
    if not currency_exists(from_currency):
        raise custom_exceptions.BadRequestError(f"The following currency does not exist: {from_currency}")

    if to_currencies is not None:
        for currency in to_currencies.split(','):
            if not currency_exists(currency):
                raise custom_exceptions.BadRequestError(f"The following currency does not exist: {currency}")

    try:
        int(amount)
    except:
        raise custom_exceptions.BadRequestError(f"The 'amount' parameter must be a number")

    try:
        date = get_formatted_date(date)
    except custom_exceptions.NonExistentDateError as err:
        raise custom_exceptions.BadRequestError(str(err))


    # -- Returning the URL parameters already validated and in the desired formatting -- #
    return {
        'from_currency': from_currency,
        'to_currencies': to_currencies,
        'amount': amount,
        'date': date
    }


def validate_interval_endpoint_params(request):

    from_currency = request.args.get("from") or 'USD'
    to_currencies = request.args.get("to")
    amount = request.args.get("amount") or '1'
    start_date = request.args.get("start_date") or datetime.now().date().isoformat()
    end_date = request.args.get("end_date") or datetime.now().date().isoformat()

    # --Validating the parameters-- #
    if not currency_exists(from_currency):
        raise custom_exceptions.BadRequestError(f"The following currency does not exist: {from_currency}")

    if to_currencies is not None:
        for currency in to_currencies.split(','):
            if not currency_exists(currency):
                raise custom_exceptions.BadRequestError(f"The following currency does not exist: {currency}")

    try:
        int(amount)
    except:
        raise custom_exceptions.BadRequestError(f"The 'amount' parameter must be a number")

    try:
        start_date = get_formatted_date(start_date)
        end_date = get_formatted_date(end_date)
    except custom_exceptions.NonExistentDateError as err:
        raise custom_exceptions.BadRequestError(str(err))

    # -- Returning the URL parameters already validated and in the desired formatting -- #
    return {
        'from_currency': from_currency,
        'to_currencies': to_currencies,
        'amount': amount,
        'start_date': start_date,
        'end_date': end_date,
    }


def consume_brapi_api(endpoint: str, params: dict, http_session: requests.Session = session) -> dict|None:
    # Just making sure the first char in the endpoint str is a /
    if endpoint[0] != "/":
        endpoint = "/" + endpoint

    url = f"{BRAPI_API_BASE_URL}{endpoint}"

    # Consuming the API
    response = http_session.get(
        url=url,
        params=params,
        timeout=10,
        headers={"Authorization": f"Bearer {os.environ['BRAPI_API_KEY']}"}
    )

    # automatically raises an exception if the HTTPS request returned an unsuccessful status code
    response.raise_for_status()

    return response.json()


def validate_quotes_endpoint_params(request) -> dict:
    tickers = request.args.get('tickers')
    analysis_time_range = request.args.get('range') or '1d'
    interval_between_quotations = request.args.get('interval') or '1m'

    # This parameter tells whether users want to include basic fundamental data such as  PE (Price-to-Earnings ratio)
    # and EPS (Earnings Per Share) in the response
    fundamental_data = request.args.get('fundamental')

    # This parameter tells whether users want to include information about dividends and interest
    # on equity historically paid by the asset in the response.
    dividends = request.args.get('dividends')

    # -- Verifications --#
    if not tickers:
        raise custom_exceptions.BadRequestError(
            "At least one stock ticker must be specified. Exemples: PETR3, GOLL54"
        )

    if not fundamental_data:
        fundamental_data = True

    if not dividends:
        dividends = True


    return {
        'tickers': tickers,
        'analysis_time_range': analysis_time_range,
        'interval_between_quotations': interval_between_quotations,
        'fundamental_data': fundamental_data,
        'dividends': dividends
    }


if __name__ == '__main__':
    print(os.environ['BRAPI_API_KEY'])