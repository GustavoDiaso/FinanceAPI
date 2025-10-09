import requests
import datetime

# External API will use
FRANKFURTER_BASE_URL = "https://api.frankfurter.dev"


def consume_frankfurter_api(endpoint: str, params: dict = None) -> dict | None:
    # Just making sure the first char in the endpoint str is a /
    if endpoint[0] != "/":
        endpoint = "/" + endpoint

    url = f"{FRANKFURTER_BASE_URL}{endpoint}"

    # Consuming the API
    response = requests.get(url, params, timeout=10)

    # automatically raises an exception if the HTTPS request returned an unsuccessful status code
    response.raise_for_status()

    return response.json()

    # except requests.HTTPError as http_err:
    #     # the HTTP status of the response was between 400-600
    #     print(f"HTTP error occurred: {http_err}")
    # except requests.ConnectionError as conn_err:
    #     print(f"Connection error occurred: {conn_err}")
    # except requests.Timeout as timeout_err:
    #     # The server didn't respond in less than 10 seconds
    #     print(f"Timeout error occurred: {timeout_err}")
    # except requests.RequestException as general_err:
    #     print(f"An error occured: {general_err}")


# print(consume_frankfurter_api("v1/latest", {'base': 'USD', 'symbols': 'EUR'}))


def get_existing_currencies() -> dict:
    currencies = {
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

    return currencies


def currency_exists(currency: str) -> bool:
    "Verifies if the given currency exists"
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


class NonExistentDateError(ValueError):
    """This error object will be raised when the Date passed to our get_formatted_date function does not exist"""

    pass


def get_formatted_date(str_date: str) -> str:
    if not date_is_real(str_date):
        raise NonExistentDateError("The given date does not exist")

    try:
        formatted_date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        return formatted_date.date().isoformat()
    except ValueError:
        formatted_date = datetime.datetime.strptime(str_date, "%d-%m-%Y")
        return formatted_date.date().isoformat()


def standardize_frankfurter_response(response: dict, success_status: bool):
    """
    The purpose of this function is to customize the frankfurter API responses by adding
    our default information and also changing some response parameters.
    """

    # Lets add the success status to the frankfurters' response
    response.update(
        {
            "success": success_status,
        }
    )

    # replace "base" with "from" in the response key
    response["from"] = response.pop("base")
    # replace "rates" with "to" in the response key
    response["to"] = response.pop("rates")
