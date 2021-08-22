import os

api_key = os.environ['SCROOGE_API_KEY']
api_host = os.environ.get('SCROOGE_API_HOST', 'apidojo-yahoo-finance-v1.p.rapidapi.com')
api_base_url = os.environ.get('SCROOGE_API_BASE_URL', 'https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2')

sql_uri = os.environ.get('SCROOGE_SQL_URI', 'postgresql+psycopg2://postgres@localhost/postgres')
