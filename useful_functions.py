import requests
import datetime
import custom_exceptions

# External API will use
FRANKFURTER_BASE_URL = "https://api.frankfurter.dev"

# Establishing our http session to send requests
session = requests.Session()


def consume_frankfurter_api(
    endpoint: str, params: dict = None, http_session: requests.Session = session
) -> dict | None:
    # Just making sure the first char in the endpoint str is a /
    if endpoint[0] != "/":
        endpoint = "/" + endpoint

    url = f"{FRANKFURTER_BASE_URL}{endpoint}"

    # Consuming the API
    response = http_session.get(url, params=params, timeout=10)

    # automatically raises an exception if the HTTPS request returned an unsuccessful status code
    response.raise_for_status()

    return response.json()


# print(consume_frankfurter_api("v1/latest", {'base': 'USD', 'symbols': 'EUR'}))


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
            datetime.datetime.strptime(str_date, date_format)
            return True
        except ValueError:
            continue

    return False


def get_formatted_date(str_date: str) -> str:
    if not date_is_real(str_date):
        raise custom_exceptions.NonExistentDateError("The given date does not exist")

    try:
        formatted_date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
    except ValueError:
        formatted_date = datetime.datetime.strptime(str_date, "%d-%m-%Y")

    return formatted_date.date().isoformat()
