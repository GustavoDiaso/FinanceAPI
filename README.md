Finance API 

Overview:
This is a simple API built with Flask that provides currency conversions and stock quotes from the Brazilian 
stock exchange (B3)

Requirements

* Python 3.11+
* pip 
* Flask 3.1.2+
* Flask-Caching 2.3.1+
* requests 2.32.3+
* python-dotenv 1.0.1+
* cachetools 6.2.1
* waitress 3.0.2 (Optional. WSGI server for production)

Configurations

1 - Clone the repository: 
```git clone https://github.com/GustavoDiaso/FinanceAPI.git```

2 - Create and activate a virtual environment (recommended)
    
* Windows: 
```
python -m venv .venv
.\.venv\Scripts\activate
```

* Linux: 
```
python3 -m venv venv
source .venv/bin/activate
```

3 - Install project dependencies from requirements.txt 

``pip install -r requirements.txt``

4 - Run the main module

* Your API will be running at: http://localhost:5000

5 - Take a quick look at the API documentation through the following endpoint: http://localhost:5000/apidocs