"""
Quotes Service - Fetches real-time stock prices, commodities, and crypto prices
Uses Finnhub API, BRAPI for Brazilian stocks, and cryptocurrency APIs
"""

import os
import requests
from urllib.parse import quote
from datetime import datetime
from typing import List, Dict, Optional
from ..utils.logger import get_logger

logger = get_logger('mirofish.services.quotes')

class QuotesService:
    """Service to fetch real-time quotes and prices"""
    
    # Finnhub API key from environment
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    BRAPI_TOKEN = os.getenv('BRAPI_TOKEN', '')
    
    # Quote symbols mapping
    QUOTES = {
        'sp500': {
            'symbol': '^GSPC',
            'name': 'S&P 500',
            'source': 'yahoo',
            'type': 'index',
            'currency': 'USD'
        },
        'dowjones': {
            'symbol': '^DJI',
            'name': 'Dow Jones',
            'source': 'yahoo',
            'type': 'index',
            'currency': 'USD'
        },
        'ibovespa': {
            'symbol': '^BVSP',
            'name': 'IBOVESPA',
            'source': 'yahoo',
            'type': 'index',
            'currency': 'BRL'
        },
        'dolar': {
            'symbol': 'BRL=X',
            'name': 'Dólar/Real',
            'source': 'yahoo',
            'type': 'currency',
            'currency': 'BRL'
        },
        'brent': {
            'symbol': 'BZ=F',
            'name': 'Petróleo Brent',
            'source': 'yahoo',
            'type': 'commodity',
            'currency': 'USD'
        },
        'ouro': {
            'symbol': 'GC=F',
            'name': 'Ouro (USD/onça)',
            'source': 'yahoo',
            'type': 'commodity',
            'currency': 'USD'
        },
        'bitcoin': {
            'symbol': 'BTC-USD',
            'name': 'Bitcoin',
            'source': 'yahoo',
            'type': 'crypto',
            'currency': 'USD'
        }
    }
    
    @staticmethod
    def fetch_quote(quote_key: str) -> Optional[Dict]:
        """
        Fetch a single quote
        
        Args:
            quote_key: Key from QUOTES dict (e.g., 'ibovespa', 'sp500', 'bitcoin')
        
        Returns:
            Dict with quote data or None if error
        """
        if quote_key not in QuotesService.QUOTES:
            logger.error(f"Unknown quote key: {quote_key}")
            return None
        
        quote_info = QuotesService.QUOTES[quote_key]
        source = quote_info['source']
        
        try:
            if source == 'yahoo':
                return QuotesService._fetch_yahoo_quote(quote_key, quote_info)
            elif source == 'finnhub':
                return QuotesService._fetch_finnhub_quote(quote_info)
            elif source == 'brapi':
                return QuotesService._fetch_brapi_quote(quote_info)
            elif source == 'crypto':
                return QuotesService._fetch_crypto_quote(quote_info)
            else:
                logger.error(f"Unknown source: {source}")
                return None
        except Exception as e:
            logger.error(f"Error fetching quote {quote_key}: {str(e)}")
            return None
    
    @staticmethod
    def fetch_all_quotes() -> List[Dict]:
        """Fetch all configured quotes"""
        quotes = []
        for key in QuotesService.QUOTES.keys():
            quote = QuotesService.fetch_quote(key)
            if quote:
                quotes.append(quote)
        return quotes

    @staticmethod
    def _fetch_yahoo_quote(quote_key: str, quote_info: Dict) -> Optional[Dict]:
        """Fetch quote from Yahoo Finance chart endpoint (no API key required)."""
        try:
            encoded_symbol = quote(quote_info['symbol'], safe='')
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}'
            params = {
                'range': '1d',
                'interval': '1m'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = data.get('chart', {}).get('result') or []
            if not result:
                logger.warning(f"No Yahoo Finance data for {quote_info['symbol']}")
                return None

            chart = result[0]
            meta = chart.get('meta', {})
            indicators = chart.get('indicators', {}).get('quote') or [{}]
            quote_values = indicators[0]

            price = meta.get('regularMarketPrice')
            previous_close = meta.get('chartPreviousClose') or meta.get('previousClose')
            high_values = [v for v in quote_values.get('high', []) if v is not None]
            low_values = [v for v in quote_values.get('low', []) if v is not None]
            open_values = [v for v in quote_values.get('open', []) if v is not None]

            if price is None:
                close_values = chart.get('indicators', {}).get('quote', [{}])[0].get('close', [])
                valid_close = [v for v in close_values if v is not None]
                price = valid_close[-1] if valid_close else None

            if price is None:
                logger.warning(f"No current price for {quote_info['symbol']}")
                return None

            change = None
            change_percent = None
            if previous_close:
                change = price - previous_close
                change_percent = (change / previous_close) * 100

            return {
                'key': quote_key,
                'symbol': quote_info['symbol'],
                'name': quote_info['name'],
                'price': price,
                'high': max(high_values) if high_values else None,
                'low': min(low_values) if low_values else None,
                'open': open_values[0] if open_values else None,
                'previous_close': previous_close,
                'change': change,
                'change_percent': change_percent,
                'timestamp': datetime.now().isoformat(),
                'source': 'yahoo',
                'type': quote_info['type'],
                'currency': quote_info['currency']
            }
        except Exception as e:
            logger.error(f"Yahoo Finance error for {quote_info['symbol']}: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_finnhub_quote(quote_info: Dict) -> Optional[Dict]:
        """Fetch quote from Finnhub API"""
        if not QuotesService.FINNHUB_API_KEY:
            logger.warning("Finnhub API key not configured")
            return None
        
        try:
            # Finnhub quote endpoint
            url = 'https://finnhub.io/api/v1/quote'
            params = {
                'symbol': quote_info['symbol'],
                'token': QuotesService.FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'c' not in data:  # current price
                logger.warning(f"No price data for {quote_info['symbol']}")
                return None
            
            return {
                'key': next(k for k, v in QuotesService.QUOTES.items() if v['symbol'] == quote_info['symbol']),
                'symbol': quote_info['symbol'],
                'name': quote_info['name'],
                'price': data.get('c'),  # current price
                'high': data.get('h'),   # high
                'low': data.get('l'),    # low
                'open': data.get('o'),   # open
                'previous_close': data.get('pc'),  # previous close
                'change': data.get('c', 0) - data.get('pc', 0),
                'change_percent': ((data.get('c', 0) - data.get('pc', 0)) / data.get('pc', 1)) * 100 if data.get('pc') else 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'finnhub',
                'type': quote_info['type'],
                'currency': quote_info['currency']
            }
        except Exception as e:
            logger.error(f"Finnhub error: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_brapi_quote(quote_info: Dict) -> Optional[Dict]:
        """Fetch quote from BRAPI (Brazilian API)"""
        if not QuotesService.BRAPI_TOKEN:
            logger.warning("BRAPI token not configured")
            return None
        
        try:
            # BRAPI quote endpoint
            url = 'https://brapi.dev/api/quote/list'
            params = {
                'token': QuotesService.BRAPI_TOKEN,
                'search': quote_info['symbol']
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('stocks'):
                logger.warning(f"No price data for {quote_info['symbol']}")
                return None
            
            stock = data['stocks'][0]
            
            return {
                'key': next(k for k, v in QuotesService.QUOTES.items() if v['symbol'] == quote_info['symbol']),
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
        except Exception as e:
            logger.error(f"BRAPI error: {str(e)}")
            return None
    
    @staticmethod
    def _fetch_crypto_quote(quote_info: Dict) -> Optional[Dict]:
        """Fetch cryptocurrency quote from CoinGecko API (free, no key required)"""
        try:
            # CoinGecko API (free)
            url = 'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': 'bitcoin',
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'bitcoin' not in data:
                logger.warning("No Bitcoin data")
                return None
            
            btc_data = data['bitcoin']
            
            return {
                'key': 'bitcoin',
                'symbol': 'BTC',
                'name': quote_info['name'],
                'price': btc_data.get('usd'),
                'market_cap': btc_data.get('usd_market_cap'),
                'change_24h': btc_data.get('usd_24h_change'),
                'change_percent': btc_data.get('usd_24h_change'),
                'timestamp': datetime.now().isoformat(),
                'source': 'coingecko',
                'type': quote_info['type'],
                'currency': quote_info['currency']
            }
        except Exception as e:
            logger.error(f"CoinGecko error: {str(e)}")
            return None
    
    @staticmethod
    def get_available_quotes() -> List[Dict]:
        """Get list of available quotes"""
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
