from flask import Flask, jsonify, request
from waitress import serve
from datetime import datetime, timezone
import toolbox as tb

"""
endpoints 

/ -> brings informations about the API 
/v1/convert?from=X&to=Y&amount=Z&date=D-> Converts a given amount of one currency to another at a given point in time


HTML response status: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status


"""
# External APIs will use
FRANKFURTER_BASE_URL = 'https://api.frankfurter.dev/v1'

app = Flask(__name__)

@app.route('/')
def api_basic_information():
    api_basic_info = {
        'success': True,
        'api_name': 'Currency API',
        'description': 'A simple API to get real-time and historical currency quotes.',
        'author': 'Gustavo Henrique de Oliveira Dias',
        'contact': {
            'github': 'https://github.com/GustavoDiaso',
            'linkedin': 'https://github.com/GustavoDiaso',
        },
        'server_time_utc': datetime.now(timezone.utc).isoformat(),
        'getting_started': {
            'example_endpoints': [
                '/v1/convert?from=USD&to=BRL&amount=1',
                '/v1/convert?from=USD&to=BRL&amount=1&date=2025-10-12',
            ]
        }
    }
    return jsonify(api_basic_info), 200


@app.route('/v1/convert')
def convert_currency():
    """Converts a given amount of one currency to another at a given point in time"""
    from_currency = request.args.get('from')
    to_currency = request.args.get('to')
    amount = request.args.get('amount')
    date = request.args.get('date')

    # If the date is not passed, use the current date. If the date is passed, verify if it's real and put it in the
    # correct format YYYY-MM-DD
    if date is None:
        date = datetime.now().date().isoformat()
    else:
        try:
            date = tb.get_formatted_date(date)
        except tb.NonExistentDateError:
            non_existent_date_error = {
                'success': False,
                'error_message': f'The date {date} does not exist'
            }
            return jsonify(non_existent_date_error), 400



    # Verifying if all the necessary URL parameters were passed
    if all([from_currency, to_currency, amount]):

        # Defining the URL parameters which will be used to send a request to FrankFurter API
        url_params = {
            'base': from_currency,
            'symbols': to_currency,
            'amount': amount
        }
        # Lets consume the FrankFurter API to get real-time information on the conversion from one currency to another
        response = tb.consume_frankfurter_api(f"/v1/{date}", url_params)
        return jsonify(response)


    else:
        variables_not_passed_error = {
            'success': False,
            'error_message': 'The parameters "to", "from" and "amount" are mandatory'
        }
        return jsonify(variables_not_passed_error), 400



app.run(port=5000, host='localhost',debug=True)

# Use waitress to serve you API
# serve(app, host='localhost', port=8080)