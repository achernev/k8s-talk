import datetime
import requests
from celery import signature
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from celery.utils.log import get_task_logger
from . import config as c
from .celeryapp import app
from .models import Base, Stonk, Price

logger = get_task_logger(__name__)
engine = create_engine(c.sql_uri, echo=True)
Base.metadata.create_all(engine)


@app.task
def fetch_symbol_quotes(symbols: str, region: str = 'US') -> None:
    """
    Fetch information about the supplied symbol(s) from the API.
    :param symbols: A comma-separated list of symbols.
    :param region: The region where these symbols appear.
    :return: The API response dictionary.
    """
    logger.info('Fetching quotes for symbols "%s" in region "%s".', symbols, region)

    querystring = {'region': region, 'symbols': symbols}

    headers = {
        'x-rapidapi-key': c.api_key,
        'x-rapidapi-host': c.api_host
    }

    response = requests.get(f'{c.api_base_url}/get-quotes', headers=headers, params=querystring)

    if response.status_code != requests.codes.ok:
        raise RuntimeError('API response code invalid.')

    api_response = response.json()

    if 'quoteResponse' not in api_response.keys():
        raise RuntimeError('Did not find required key "quoteResponse" in API response.')

    if 'result' not in api_response['quoteResponse'].keys():
        raise RuntimeError('Did not find required key "quoteResponse.result" in API response.')

    if api_response.get('error') is not None:
        raise RuntimeError('API returned error: %s' % api_response['error'])

    if len(api_response['quoteResponse']['result']) == 0:
        raise RuntimeError('API response result is empty.')

    signature(record_prices).delay(response.json())


@app.task
def record_prices(api_response: dict) -> None:
    """
    Record the prices received from the API into database.
    :param api_response: The response from the API, verbatim.
    """
    with Session(engine, future=True) as session:
        for stonk_data in api_response['quoteResponse']['result']:
            logger.info('Recording price for symbol "%s" at "%d".',
                        stonk_data['symbol'], stonk_data['regularMarketTime'])
            stonk = session.query(Stonk).filter_by(symbol=stonk_data['symbol']).first()
            if stonk is None:
                logger.debug('Stonk "%s" not found in database, creating.', stonk_data['symbol'])
                stonk = Stonk()
                stonk.symbol = stonk_data['symbol']
                stonk.name = stonk_data['longName']
                stonk.exchange = stonk_data['exchange']
            price = Price()
            price.stonk = stonk
            price.bid = stonk_data['bid']
            price.ask = stonk_data['ask']
            price.ts = datetime.datetime.fromtimestamp(stonk_data['regularMarketTime'])
            session.add(stonk)
            session.add(price)
        session.commit()
        session.flush()
    logger.debug('Finished recording batch into database.')


@app.task
def update_prices() -> None:
    """
    Update prices for all symbols in the database.
    """
    logger.info('Updating all prices.')
    with Session(engine, future=True) as session:
        symbols = session.query(Stonk.symbol).all()
        if len(symbols) == 0:
            raise RuntimeError('No symbols found in database.')
        symbols_concat = ','.join(s[0] for s in symbols)
    signature(fetch_symbol_quotes).delay(symbols_concat)
