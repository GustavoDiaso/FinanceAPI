from flask import Flask, jsonify, request
from waitress import serve
from datetime import datetime, timezone
import useful_functions as uf
from requests import RequestException
import standard_responses as sr
import custom_exceptions

"""
HTML response status for reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
"""

app = Flask(__name__)

# -------- Exising routes ---------- #

@app.route("/")
def api_basic_information():
    api_basic_info = {
        "success": True,
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
                "/v1/historical?from=USD&to=BRL&amount=1",
                "/v1/historical?from=USD&to=BRL&amount=1&date=2025-10-12",
            ]
        },
    }
    return jsonify(api_basic_info), 200


@app.route("/v1/historical", methods=['GET'])
def historical_conversion():
    """Converts a given amount of one currency to another on a specific date"""

    from_currency = request.args.get("from")
    to_currencies = request.args.get("to")
    amount = request.args.get("amount")
    date = request.args.get("date")

    # Verifying if all the mandatory URL parameters were passed
    if from_currency:

        # If the date is not passed, use the current date. If the date is passed, verify if it's valid and put it in the
        # correct format YYYY-MM-DD
        if date is None:
            date = datetime.now().date().isoformat()
        else:
            try:
                date = uf.get_formatted_date(date)
            except custom_exceptions.NonExistentDateError:
                return (
                    jsonify(
                        sr.StandardAPIErrorMessage(
                            http_error_code=400,
                            error_message=f"The date {date} does not exist"
                        ).to_dict()
                    ),
                    400
                )

        # If the 'from' currency does not exist, raise an error
        if uf.currency_exists(from_currency) == False:
            return (
                jsonify(
                   sr.StandardAPIErrorMessage(
                       http_error_code=400,
                       error_message= f"The following currency does not exist: {from_currency}"
                   ).to_dict()
                ),
                400
            )

        # First, check if the user wants a conversion to all currencies (to_currencies = None).
        # If not, verifies if each currency passed is valid. If so, everything is ok, if not, return an error message
        if to_currencies is not None:
            for currency in to_currencies.split(','):
                if uf.currency_exists(currency) == False:
                    return (
                        jsonify(
                            sr.StandardAPIErrorMessage(
                                http_error_code=400,
                                error_message=f"The following currency does not exist: {currency}"
                            ).to_dict()
                        ),
                        400
                    )

    else:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400,
                    error_message= 'The ULR parameter "from" is mandatory'
                ).to_dict()
            ),
            400,
        )

    # Defining the URL parameters which will be used to send a request to FrankFurter API
    url_params = {
        "base": from_currency,
        "symbols": to_currencies,
        "amount": amount if amount is not None else 1,
    }
    if to_currencies is None:
        url_params.pop('symbols')

    # Lets try to consume the FrankFurter API to get real-time information on the conversion from one currency to another
    try:
        response = uf.consume_frankfurter_api(f"/v1/{date}", url_params)

        # replacing the "base" dict key with "from" in the response
        response["from"] = response.pop("base")
        # replacing the "rates" dict key with "to" in the response
        response["to"] = response.pop("rates")

        # Padronizing the response
        response = sr.StandardAPISuccessfulResponse(data=response).to_dict()

        return jsonify(response)

    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code,
                    error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code
        )


@app.route('/v1/interval', methods=['GET'])
def date_interval_conversion():
    """Converts a given amount of one currency to another within a given date range"""

    from_currency = request.args.get("from")
    to_currencies = request.args.get("to")
    amount = request.args.get("amount")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    date_interval = [start_date, end_date]

    # Verifying if all the mandatory URL parameters were passed
    if from_currency:

        for i in range(0,2):
            if date_interval[i] is None:
                date_interval[i] = datetime.now().date().isoformat()
            else:
                try:
                    date_interval[i] = uf.get_formatted_date(date_interval[i])
                except custom_exceptions.NonExistentDateError:
                    return (
                        jsonify(
                            sr.StandardAPIErrorMessage(
                                http_error_code=400,
                                error_message=f"The date {date_interval[i]} does not exist"
                            ).to_dict()
                        ),
                        400
                    )

        # If the 'from' currency does not exist, raise an error
        if uf.currency_exists(from_currency) == False:
            return (
                jsonify(
                    sr.StandardAPIErrorMessage(
                        http_error_code=400,
                        error_message=f"The following currency does not exist: {from_currency}"
                    ).to_dict()
                ),
                400
            )

        # First, check if the user wants a conversion to all currencies (to_currencies = None).
        # If not, verifies if each currency passed is valid. If so, everything is ok, if not, return an error message
        if to_currencies is not None:
            for currency in to_currencies.split(','):
                if uf.currency_exists(currency) == False:
                    return (
                        jsonify(
                            sr.StandardAPIErrorMessage(
                                http_error_code=400,
                                error_message=f"The following currency does not exist: {currency}"
                            ).to_dict()
                        ),
                        400
                    )

    else:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400,
                    error_message='The URL parameter "from" is mandatory'
                ).to_dict()
            ),
            400,
        )

    url_params = {
        "base": from_currency,
        "symbols": to_currencies,
        "amount": amount if amount is not None else 1,
    }
    if to_currencies is None:
        url_params.pop('symbols')

    # Lets try to consume the FrankFurter API to get real-time information on the conversion from one currency to another
    try:
        response = uf.consume_frankfurter_api(f"/v1/{date_interval[0]}..{date_interval[1]}", url_params)

        # replacing the "base" dict key with "from" in the response
        response["from"] = response.pop("base")
        # replacing the "rates" dict key with "to" in the response
        response["to"] = response.pop("rates")

        # Padronizing the response
        response = sr.StandardAPISuccessfulResponse(data=response).to_dict()

        return jsonify(response)

    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code,
                    error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code
        )

@app.errorhandler(404)
def not_found_error_handler(err):
    """
    This function will be called whenever there is no function linked to the endpoint of the user's request.
    (404 Not Found) error
    """
    return (
        jsonify(
            sr.StandardAPIErrorMessage(
                http_error_code=404,
                error_message=str(err)
            ).to_dict()
        ),
        404
    )

@app.errorhandler(500)
def internal_server_error_handler(err):
    return (
        jsonify(
            sr.StandardAPIErrorMessage(
                http_error_code=500,
                error_message=str(err)
            ).to_dict()
        ),
        500
    )

if __name__ == '__main__':
    app.run(port=5000, host="localhost", debug=True)

# Use waitress to serve you API
# serve(app, host='localhost', port=8080)
