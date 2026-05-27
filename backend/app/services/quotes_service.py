"""
Quotes Service - Fetches real-time market quotes using configured API keys.
Uses Finnhub for US ETFs/commodities, BRAPI for Brazilian market/currency, and CoinGecko for Bitcoin.
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.services.quotes')


class QuotesService:
    """Service to fetch real-time quotes and prices."""

    FINNHUB_API_KEY = Config.FINNHUB_API_KEY
    BRAPI_TOKEN = Config.BRAPI_TOKEN

    QUOTES = {
        'sp500': {'symbol': 'SPY', 'name': 'S&P 500', 'source': 'finnhub', 'type': 'index', 'currency': 'USD'},
        'dowjones': {'symbol': 'DIA', 'name': 'Dow Jones', 'source': 'finnhub', 'type': 'index', 'currency': 'USD'},
        'ibovespa': {'symbol': '^BVSP', 'name': 'IBOVESPA', 'source': 'brapi_yahoo_fallback', 'type': 'index', 'currency': 'BRL'},
        'dolar': {'symbol': 'USD-BRL', 'name': 'Dólar/Real', 'source': 'brapi_currency', 'type': 'currency', 'currency': 'BRL'},
        'brent': {'symbol': 'BZ', 'name': 'Petróleo Brent', 'source': 'finnhub', 'type': 'commodity', 'currency': 'USD'},
        'ouro': {'symbol': 'GLD', 'name': 'Ouro (USD/onça)', 'source': 'finnhub_yahoo_fallback', 'type': 'commodity', 'currency': 'USD'},
        'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'source': 'crypto', 'type': 'crypto', 'currency': 'USD'}
    }

    @staticmethod
    def fetch_quote(quote_key: str) -> Optional[Dict]:
        """Fetch a single quote by key."""
        quote_info = QuotesService.QUOTES.get(quote_key)
        if not quote_info:
            logger.error(f"Unknown quote key: {quote_key}")
            return None

        source = quote_info['source']
        try:
            if source == 'finnhub':
                return QuotesService._fetch_finnhub_quote(quote_key, quote_info)
            if source == 'finnhub_yahoo_fallback':
                quote = QuotesService._fetch_finnhub_quote(quote_key, quote_info)
                if quote:
                    return quote
                yahoo_quote_info = {**quote_info, 'symbol': 'GC=F'}
                return QuotesService._fetch_yahoo_quote(quote_key, yahoo_quote_info)
            if source == 'brapi':
                return QuotesService._fetch_brapi_quote(quote_key, quote_info)
            if source == 'brapi_yahoo_fallback':
                quote = QuotesService._fetch_brapi_quote(quote_key, quote_info)
                return quote or QuotesService._fetch_yahoo_quote(quote_key, quote_info)
            if source == 'brapi_currency':
                return QuotesService._fetch_brapi_currency(quote_key, quote_info)
            if source == 'crypto':
                return QuotesService._fetch_crypto_quote(quote_key, quote_info)

            logger.error(f"Unknown quote source: {source}")
            return None
        except Exception as e:
            logger.error(f"Error fetching quote {quote_key}: {str(e)}")
            return None

    @staticmethod
    def fetch_all_quotes() -> List[Dict]:
        """Fetch all configured quotes."""
        quotes = []
        for key in QuotesService.QUOTES:
            quote = QuotesService.fetch_quote(key)
            if quote and quote.get('price') is not None:
                quotes.append(quote)
        return quotes

    @staticmethod
    def _fetch_finnhub_quote(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fetch quote from Finnhub API."""
        if not QuotesService.FINNHUB_API_KEY:
            logger.warning("Finnhub API key not configured")
            return None

        response = requests.get(
            'https://finnhub.io/api/v1/quote',
            params={'symbol': quote_info['symbol'], 'token': QuotesService.FINNHUB_API_KEY},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        price = data.get('c')
        previous_close = data.get('pc')
        if not price:
            logger.warning(f"No Finnhub price for {quote_info['symbol']}: {data}")
            return None

        change = data.get('d')
        if change is None and previous_close:
            change = price - previous_close

        change_percent = data.get('dp')
        if change_percent is None and previous_close:
            change_percent = (change / previous_close) * 100

        return {
            'key': quote_key,
            'symbol': quote_info['symbol'],
            'name': quote_info['name'],
            'price': price,
            'high': data.get('h'),
            'low': data.get('l'),
            'open': data.get('o'),
            'previous_close': previous_close,
            'change': change,
            'change_percent': change_percent,
            'timestamp': datetime.now().isoformat(),
            'source': 'finnhub',
            'type': quote_info['type'],
            'currency': quote_info['currency']
        }

    @staticmethod
    def _fetch_brapi_quote(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fetch quote from BRAPI."""
        if not QuotesService.BRAPI_TOKEN:
            logger.warning("BRAPI token not configured")
            return None

        response = requests.get(
            'https://brapi.dev/api/quote/list',
            params={'search': quote_info['symbol'], 'token': QuotesService.BRAPI_TOKEN},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        stocks = data.get('stocks') or []
        if not stocks:
            logger.warning(f"No BRAPI stock data for {quote_info['symbol']}: {data}")
            return None

        stock = stocks[0]
        return {
            'key': quote_key,
            'symbol': quote_info['symbol'],
            'name': quote_info['name'],
            'price': stock.get('regularMarketPrice'),
            'high': stock.get('regularMarketDayHigh'),
            'low': stock.get('regularMarketDayLow'),
            'open': stock.get('regularMarketOpen'),
            'previous_close': stock.get('regularMarketPreviousClose'),
            'change': stock.get('regularMarketChange'),
            'change_percent': stock.get('regularMarketChangePercent'),
            'timestamp': datetime.now().isoformat(),
            'source': 'brapi',
            'type': quote_info['type'],
            'currency': quote_info['currency']
        }

    @staticmethod
    def _fetch_brapi_currency(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fetch currency quote from BRAPI, with AwesomeAPI fallback."""
        if not QuotesService.BRAPI_TOKEN:
            logger.warning("BRAPI token not configured")
            return QuotesService._fetch_awesome_currency(quote_key, quote_info)

        try:
            response = requests.get(
                'https://brapi.dev/api/v2/currency',
                params={'currency': quote_info['symbol'], 'token': QuotesService.BRAPI_TOKEN},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            currency_data = data.get('currency') or []
            if not currency_data:
                logger.warning(f"No BRAPI currency data for {quote_info['symbol']}: {data}")
                return QuotesService._fetch_awesome_currency(quote_key, quote_info)

            item = currency_data[0]
            price = item.get('bidPrice') or item.get('askPrice')
            return {
                'key': quote_key,
                'symbol': quote_info['symbol'],
                'name': quote_info['name'],
                'price': float(price) if price is not None else None,
                'high': float(item['high']) if item.get('high') is not None else None,
                'low': float(item['low']) if item.get('low') is not None else None,
                'open': None,
                'previous_close': None,
                'change': float(item['bidVariation']) if item.get('bidVariation') is not None else None,
                'change_percent': float(item['pctChange']) if item.get('pctChange') is not None else None,
                'timestamp': datetime.now().isoformat(),
                'source': 'brapi',
                'type': quote_info['type'],
                'currency': quote_info['currency']
            }
        except Exception as e:
            logger.warning(f"BRAPI currency failed for {quote_info['symbol']}: {str(e)}")
            return QuotesService._fetch_awesome_currency(quote_key, quote_info)

    @staticmethod
    def _fetch_awesome_currency(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fallback currency quote from AwesomeAPI."""
        response = requests.get(
            'https://economia.awesomeapi.com.br/json/last/USD-BRL',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        item = data.get('USDBRL')
        if not item:
            logger.warning(f"No AwesomeAPI currency data: {data}")
            return None

        return {
            'key': quote_key,
            'symbol': quote_info['symbol'],
            'name': quote_info['name'],
            'price': float(item['bid']) if item.get('bid') is not None else None,
            'high': float(item['high']) if item.get('high') is not None else None,
            'low': float(item['low']) if item.get('low') is not None else None,
            'open': float(item['open']) if item.get('open') is not None else None,
            'previous_close': None,
            'change': float(item['varBid']) if item.get('varBid') is not None else None,
            'change_percent': float(item['pctChange']) if item.get('pctChange') is not None else None,
            'timestamp': datetime.now().isoformat(),
            'source': 'awesomeapi',
            'type': quote_info['type'],
            'currency': quote_info['currency']
        }

    @staticmethod
    def _fetch_yahoo_quote(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fallback quote from Yahoo Finance."""
        response = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{quote_info['symbol']}",
            params={'range': '1d', 'interval': '1m'},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        result = data.get('chart', {}).get('result') or []
        if not result:
            logger.warning(f"No Yahoo data for {quote_info['symbol']}: {data}")
            return None

        chart = result[0]
        meta = chart.get('meta', {})
        price = meta.get('regularMarketPrice')
        previous_close = meta.get('chartPreviousClose') or meta.get('previousClose')
        if price is None:
            logger.warning(f"No Yahoo price for {quote_info['symbol']}")
            return None

        change = (price - previous_close) if previous_close else None
        change_percent = ((change / previous_close) * 100) if previous_close and change is not None else None
        return {
            'key': quote_key,
            'symbol': quote_info['symbol'],
            'name': quote_info['name'],
            'price': price,
            'high': meta.get('regularMarketDayHigh'),
            'low': meta.get('regularMarketDayLow'),
            'open': meta.get('regularMarketOpen'),
            'previous_close': previous_close,
            'change': change,
            'change_percent': change_percent,
            'timestamp': datetime.now().isoformat(),
            'source': 'yahoo',
            'type': quote_info['type'],
            'currency': quote_info['currency']
        }

    @staticmethod
    def _fetch_crypto_quote(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fetch Bitcoin quote from CoinGecko."""
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin',
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_change': 'true'
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        btc_data = data.get('bitcoin')
        if not btc_data:
            logger.warning(f"No Bitcoin data: {data}")
            return None

        return {
            'key': quote_key,
            'symbol': quote_info['symbol'],
            'name': quote_info['name'],
            'price': btc_data.get('usd'),
            'market_cap': btc_data.get('usd_market_cap'),
            'change': None,
            'change_percent': btc_data.get('usd_24h_change'),
            'timestamp': datetime.now().isoformat(),
            'source': 'coingecko',
            'type': quote_info['type'],
            'currency': quote_info['currency']
        }

    @staticmethod
    def get_available_quotes() -> List[Dict]:
        """Get list of available quotes."""
        return [
            {
                'key': key,
                'name': info['name'],
                'symbol': info['symbol'],
                'type': info['type'],
                'currency': info['currency'],
                'source': info['source']
            }
            for key, info in QuotesService.QUOTES.items()
        ]