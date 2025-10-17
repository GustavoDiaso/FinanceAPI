from flask import Flask, jsonify, request
from flask_caching import Cache
from flasgger import Swagger, swag_from
# from waitress import serve
from requests import RequestException

# -- Personal modules -- #
import custom_exceptions
import useful_functions as uf
import standard_responses as sr
import configurations as configs
import templates

"""
HTML response status for reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
"""
app = Flask(__name__)

# Adding some default configs to the Flask API instance
app.config.from_mapping(configs.default_flask_api_config)

cache = Cache(app)

swagger = Swagger(app, template=templates.swagger_template)

# -------- Existing routes ---------- #

@app.route("/")
@swag_from("docs/api_info_endpoint.yml")
def api_basic_information():
    return (
        jsonify(
            sr.StandardAPISuccessfulResponse(data=uf.get_api_basic_info()).to_dict()
        ),
        200,
    )


@app.route("/v1/conversion/historical", methods=["GET"])
@cache.cached(query_string=True)
@swag_from("docs/conversion_historical.yml")
def historical_conversion():
    """Converts a given amount of one currency to another on a specific date"""

    try:
        # Getting the URL parameters passed in the request to the historical endpoin pre-formatted and ready-to-use
        params = uf.validate_historical_endpoint_params(request)
    except custom_exceptions.BadRequestError as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400, error_message=str(err)
                ).to_dict()
            ),
            400,
        )

    # Lets try to consume the FrankFurter API to get real-time information on the conversion from one currency to another
    try:
        # Defining the URL parameters which will be used to send a request to FrankFurter API
        url_params = {
            "base": params["from_currency"],
            "symbols": params["to_currencies"],
            "amount": params["amount"],
        }

        #  Only the parameters different than None will be passed to the FrankFurter API request
        response = uf.consume_frankfurter_api(
            endpoint=f"/v1/{params['date']}",
            params={
                key: value for key, value in url_params.items() if value is not None
            },
        )

        # replacing the "base" dict key with "from" in the response
        response["from"] = response.pop("base")
        # replacing the "rates" dict key with "to" in the response
        response["to"] = response.pop("rates")

        # Returning the padronized response
        return (jsonify(sr.StandardAPISuccessfulResponse(data=response).to_dict()), 200)

    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code, error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code,
        )


@app.route("/v1/conversion/interval", methods=["GET"])
@cache.cached(query_string=True)
@swag_from("docs/conversion_interval.yml")
def date_interval_conversion():
    """Converts a given amount of one currency to another within a given date range"""

    try:
        # Getting the URL parameters passed in the request to the interval endpoin pre-formatted and ready-to-use
        params = uf.validate_interval_endpoint_params(request)

    except custom_exceptions.BadRequestError as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400, error_message=str(err)
                ).to_dict()
            ),
            400,
        )

    # Lets try to consume the FrankFurter API to get real-time information on the conversion from one currency to another
    try:
        url_params = {
            "base": params["from_currency"],
            "symbols": params["to_currencies"],
            "amount": params["amount"],
        }

        #  Only the parameters different than None will be passed to the FrankFurter API request
        response = uf.consume_frankfurter_api(
            endpoint=f"/v1/{params['start_date']}..{params['end_date']}",
            params={
                key: value for key, value in url_params.items() if value is not None
            },
        )

        # replacing the "base" dict key with "from" in the response
        response["from"] = response.pop("base")
        # replacing the "rates" dict key with "to" in the response
        response["to"] = response.pop("rates")

        # Returning the padronized response
        return (jsonify(sr.StandardAPISuccessfulResponse(data=response).to_dict()), 200)

    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code, error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code,
        )


@app.route("/v1/currencies", methods=["GET"])
@swag_from("docs/currencies.yml")
def get_currencies():
    """This function returns all the currencies we are able to convert"""
    return (
        jsonify(
            sr.StandardAPISuccessfulResponse(
                data=uf.get_existing_currencies()
            ).to_dict()
        ),
        200,
    )


@app.route("/v1/b3stocks/all", methods=["GET"])
@swag_from("docs/b3stocks_all.yml")
def get_all_b3stocks():
    """This function returns the tickers of all stocks traded on B3 at the present time"""
    try:
        return (
            jsonify(
                sr.StandardAPISuccessfulResponse(data=uf.get_b3_traded_stocks()).to_dict()
            ),
            200,
        )

    except custom_exceptions.MissingBrapiAPIKeyError as err:
        print(str(err))
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=503,
                    error_message="This endpoint is unavailable at the moment. Please try again later.",
                ).to_dict()
            ),
            503,
        )
    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code, error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code,
        )


@app.route("/v1/b3stocks/quote", methods=["GET"])
@cache.cached(timeout=900, query_string=True)  # caching the quote results for 15 mintues. This is not a DayTrade API
@swag_from("docs/b3stocks_quote.yml")
def get_b3stocks_quotes():
    """This funtion returns the quote of a given B3 stock"""
    try:
        # Getting the URL parameters passed in the request to the quote endpoin pre-formatted and ready-to-use
        params = uf.validate_quotes_endpoint_params(request)

    except custom_exceptions.BadRequestError as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400, error_message=str(err)
                ).to_dict()
            ),
            400,
        )
    except custom_exceptions.MissingBrapiAPIKeyError as err:
        print(str(err))
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=503,
                    error_message="This endpoint is unavailable at the moment. Please try again later.",
                ).to_dict()
            ),
            503,
        )

    try:
        url_params = {
            "range": params["analysis_time_range"],
            "interval": params["interval_between_quotations"],
            "fundamental": params["fundamental_data"],
            "dividends": params["dividends"],
        }
        response = uf.consume_brapi_api(
            endpoint=f"quote/{params['ticker']}",
            params={
                key: value for key, value in url_params.items() if value is not None
            },
        )

        return (
            jsonify(
                sr.StandardAPISuccessfulResponse(data=response["results"]).to_dict()
            ),
            200,
        )

    except custom_exceptions.InvalidBrapiAPIKeyError as err:
        print(str(err))
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=503,
                    error_message="This endpoint is unavailable at the moment. Please try again later.",
                ).to_dict()
            ),
            503,
        )
    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code, error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code,
        )


@app.route("/v1/b3stocks/stocksinfo", methods=["GET"])
@cache.cached(timeout=900, query_string=True)
@swag_from("docs/b3stocks_stocksinfo.yml")
def get_b3stocks_information():
    """This function returns information about stocks traded on b3"""
    try:
        # Getting the URL parameters passed in the request to the stocksinfo endpoin pre-formatted and ready-to-use
        params = uf.validate_stocksinfo_endpoint_params(request)

    except custom_exceptions.BadRequestError as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=400, error_message=str(err)
                ).to_dict()
            ),
            400,
        )

    try:
        url_params = {
            "sector": params["sector"],
            "sortBy": params["sortedBy"],
            "sortOrder": params["order"],
            "limit": params["limit"],
            "page": params["page"],
            "type": "stock",
        }

        # Only the URL parameters different than None will be passed to the brapi API request
        response = uf.consume_brapi_api(
            endpoint="/quote/list",
            params={
                key: value for key, value in url_params.items() if value is not None
            },
        )

        # -- adding additional informations in the response to guide the user in next requests -- #
        response.pop("availableStockTypes")
        response["sortByOptions"] = [
            "name",
            "close",
            "change",
            "change_abs",
            "volume",
            "market_cap_basic",
            "sector"
        ]

        return (jsonify(sr.StandardAPISuccessfulResponse(data=response).to_dict()), 200)

    except (
        custom_exceptions.MissingBrapiAPIKeyError,
        custom_exceptions.InvalidBrapiAPIKeyError,
    ) as err:
        print(str(err))
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=503,
                    error_message="This endpoint is unavailable at the moment. Please try again later.",
                ).to_dict()
            ),
            503,
        )

    except RequestException as err:
        return (
            jsonify(
                sr.StandardAPIErrorMessage(
                    http_error_code=err.response.status_code, error_message=str(err)
                ).to_dict()
            ),
            err.response.status_code,
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
                http_error_code=404, error_message=str(err)
            ).to_dict()
        ),
        404,
    )


@app.errorhandler(500)
def internal_server_error_handler(err):
    return (
        jsonify(
            sr.StandardAPIErrorMessage(
                http_error_code=500, error_message=str(err)
            ).to_dict()
        ),
        500,
    )


if __name__ == "__main__":
    app.run(port=5000, host="localhost", debug=True)

# Use waitress to serve you API
# serve(app, host='localhost', port=8080)
