from flask import Flask, jsonify, request
#from waitress import serve
import useful_functions as uf
from requests import RequestException
import standard_responses as sr
import custom_exceptions

"""
HTML response status for reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
"""

app = Flask(__name__)

# -------- Existing routes ---------- #

@app.route("/")
def api_basic_information():
    return (
        jsonify(
            sr.StandardAPISuccessfulResponse(data=uf.get_api_basic_info()).to_dict()
        ),
        200
    )

@app.route("/v1/historical", methods=['GET'])
def historical_conversion():
    """Converts a given amount of one currency to another on a specific date"""

    try:
        # This function validates the URL parameters passed in the request and returns them pre-formatted so they can be
        # processed. If any passed parameter doesn't match what was expected, the function raises an error.
        params = uf.validate_historical_endpoint_params(request)
    except custom_exceptions.BadRequestError as err:
        return (
            jsonify(
               sr.StandardAPIErrorMessage(
                   http_error_code=400,
                   error_message=str(err)
               ).to_dict()
            ),
            400
        )

    #Lets try to consume the FrankFurter API to get real-time information on the conversion from one currency to another
    try:
        # Defining the URL parameters which will be used to send a request to FrankFurter API
        url_params = {
            "base": params['from_currency'],
            "symbols": params['to_currencies'],
            "amount": params['amount'],
        }
        if url_params['symbols'] is None:
            url_params.pop('symbols')

        response = uf.consume_frankfurter_api(f"/v1/{params['date']}", url_params)

        # replacing the "base" dict key with "from" in the response
        response["from"] = response.pop("base")
        # replacing the "rates" dict key with "to" in the response
        response["to"] = response.pop("rates")

        # Returning the padronized response
        return (
            jsonify(
                sr.StandardAPISuccessfulResponse(data=response).to_dict()
            ), 200
        )

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

    try:
        # This function validates the URL parameters passed in the request and returns them pre-formatted so they can be
        # processed. If any passed parameter doesn't match what was expected, the function raises an error.
        params = uf.validate_interval_endpoint_params(request)
    except custom_exceptions.BadRequestError as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400,
                    error_message=str(err)
                ).to_dict()
            ),
            400
        )

    #Lets try to consume the FrankFurter API to get real-time information on the conversion from one currency to another
    try:
        url_params = {
            "base": params['from_currency'],
            "symbols": params['to_currencies'],
            "amount": params['amount'],
        }
        if url_params['symbols'] is None:
            url_params.pop('symbols')

        response = uf.consume_frankfurter_api(f"/v1/{params['start_date']}..{params['end_date']}", url_params)

        # replacing the "base" dict key with "from" in the response
        response["from"] = response.pop("base")
        # replacing the "rates" dict key with "to" in the response
        response["to"] = response.pop("rates")

        # Returning the padronized response
        return (
            jsonify(
                sr.StandardAPISuccessfulResponse(data=response).to_dict()
            ),
            200
        )

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

@app.route('/v1/currencies', methods=['GET'])
def get_currencies():
    return (
        jsonify(
            sr.StandardAPISuccessfulResponse(data=uf.get_existing_currencies()).to_dict()
        ),
        200
    )

# -------- Handling errors ---------- #

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
