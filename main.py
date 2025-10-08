from flask import Flask, jsonify, request
from waitress import serve
from datetime import datetime, timezone

"""
endpoints 

/ -> brings informations about the API 


"""

app = Flask(__name__)

@app.route('/')
def api_basic_information():
    api_basic_info = {
        'api_name': 'Currency API',
        'description': 'A simple API to get real-time and historical currency quotes.',
        'author': 'Gustavo Henrique de Oliveira Dias',
        'contact': {
            'github': 'https://github.com/GustavoDiaso',
            'linkedin': 'https://github.com/GustavoDiaso',
        },
        'server_time_utc': datetime.now(timezone.utc).isoformat(),
        'getting_started': {
            'example_endpoints': {
                ""
            }
        }

    }




app.run(port=5000, host='localhost',debug=True)

# Use waitress to serve you API
# serve(app, host='localhost', port=8080)