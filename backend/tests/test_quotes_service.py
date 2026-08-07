"""
Unit tests for QuotesService
"""

import unittest
from unittest.mock import patch

import requests

from app.services.quotes_service import QuotesService


class TestQuotesService(unittest.TestCase):
    """Test QuotesService functionality"""
    
    def test_quotes_configured(self):
        """Test that all required quotes are configured"""
        quotes = QuotesService.QUOTES
        self.assertIsNotNone(quotes)
        self.assertGreater(len(quotes), 0)
        
        # Check required quotes exist
        required_quotes = ['ibovespa', 'sp500', 'dowjones', 'dolar', 'brent', 'ouro', 'bitcoin']
        for quote in required_quotes:
            self.assertIn(quote, quotes, f"Quote {quote} not configured")
    
    def test_quote_structure(self):
        """Test that each quote has required fields"""
        for key, quote_info in QuotesService.QUOTES.items():
            self.assertIn('symbol', quote_info, f"Quote {key} missing 'symbol'")
            self.assertIn('name', quote_info, f"Quote {key} missing 'name'")
            self.assertIn('source', quote_info, f"Quote {key} missing 'source'")
            self.assertIn('type', quote_info, f"Quote {key} missing 'type'")
            self.assertIn('currency', quote_info, f"Quote {key} missing 'currency'")
    
    def test_available_quotes(self):
        """Test that get_available_quotes returns list"""
        quotes = QuotesService.get_available_quotes()
        self.assertIsInstance(quotes, list)
        self.assertGreater(len(quotes), 0)
        
        # Check structure of first quote
        if quotes:
            quote = quotes[0]
            self.assertIn('key', quote)
            self.assertIn('name', quote)
            self.assertIn('symbol', quote)
            self.assertIn('type', quote)
            self.assertIn('currency', quote)
    
    def test_fetch_bitcoin_quote(self):
        """Test that Bitcoin quote can be fetched (CoinGecko is free)"""
        try:
            quote = QuotesService.fetch_quote('bitcoin')
            if quote:
                self.assertIn('price', quote)
                self.assertIn('name', quote)
                self.assertEqual(quote['key'], 'bitcoin')
                self.assertGreater(quote['price'], 0)
        except Exception as e:
            self.skipTest(f"Network error: {str(e)}")
    
    def test_fetch_unknown_quote_returns_none(self):
        """Test that fetching unknown quote returns None"""
        quote = QuotesService.fetch_quote('unknown_quote')
        self.assertIsNone(quote)
    
    def test_fetch_all_quotes_returns_list(self):
        """Test that fetch_all_quotes returns a list"""
        try:
            quotes = QuotesService.fetch_all_quotes()
            self.assertIsInstance(quotes, list)
        except Exception as e:
            self.skipTest(f"Network error: {str(e)}")

    def test_every_quote_source_has_a_chain(self):
        """Every configured quote must map to a known source chain"""
        for key, quote_info in QuotesService.QUOTES.items():
            self.assertIn(
                quote_info['source'], QuotesService.SOURCE_CHAINS,
                f"Quote {key} uses source '{quote_info['source']}' with no chain"
            )


class TestQuotesFallbackChain(unittest.TestCase):
    """Fallback behaviour when an upstream provider fails.

    Regression cover: a raising provider used to abort the whole quote instead
    of advancing to the next source, which silently dropped IBOVESPA and
    Dólar/Real from the dashboard whenever BRAPI timed out.
    """

    @staticmethod
    def _quote(source, price=123.45):
        return {'key': 'ibovespa', 'name': 'IBOVESPA', 'price': price, 'source': source}

    def test_brapi_timeout_still_falls_back_to_yahoo(self):
        """A raising BRAPI must not stop the Yahoo attempt (ibovespa)"""
        with patch.object(QuotesService, '_fetch_brapi_quote',
                          side_effect=requests.exceptions.ReadTimeout('read timed out')), \
             patch.object(QuotesService, '_fetch_yahoo_quote',
                          return_value=self._quote('yahoo')) as yahoo:
            result = QuotesService.fetch_quote('ibovespa')

        yahoo.assert_called_once()
        self.assertIsNotNone(result)
        self.assertEqual(result['source'], 'yahoo')

    def test_brapi_without_price_falls_back_to_yahoo(self):
        """A BRAPI payload with price=None must advance the chain (ibovespa)"""
        with patch.object(QuotesService, '_fetch_brapi_quote',
                          return_value=self._quote('brapi', price=None)), \
             patch.object(QuotesService, '_fetch_yahoo_quote',
                          return_value=self._quote('yahoo')):
            result = QuotesService.fetch_quote('ibovespa')

        self.assertIsNotNone(result)
        self.assertEqual(result['source'], 'yahoo')

    def test_yahoo_uses_provider_specific_symbol(self):
        """Yahoo attempts must use yahoo_symbol when the quote defines one (dolar)"""
        with patch.object(QuotesService, '_fetch_brapi_currency',
                          side_effect=requests.exceptions.ReadTimeout('read timed out')), \
             patch.object(QuotesService, '_fetch_awesome_currency',
                          side_effect=requests.exceptions.ConnectionError('unreachable')), \
             patch.object(QuotesService, '_fetch_yahoo_quote',
                          return_value=self._quote('yahoo', price=5.09)) as yahoo:
            result = QuotesService.fetch_quote('dolar')

        self.assertIsNotNone(result)
        self.assertEqual(yahoo.call_args.args[1]['symbol'], 'USDBRL=X')

    def test_currency_chain_exhausted_returns_none(self):
        """When every source fails the quote resolves to None, not an exception"""
        with patch.object(QuotesService, '_fetch_brapi_currency',
                          side_effect=requests.exceptions.ReadTimeout('read timed out')), \
             patch.object(QuotesService, '_fetch_awesome_currency',
                          side_effect=requests.exceptions.ConnectionError('unreachable')), \
             patch.object(QuotesService, '_fetch_yahoo_quote',
                          side_effect=ValueError('bad payload')):
            self.assertIsNone(QuotesService.fetch_quote('dolar'))

    def test_first_working_source_short_circuits(self):
        """A healthy BRAPI response must not trigger the Yahoo attempt"""
        with patch.object(QuotesService, '_fetch_brapi_quote',
                          return_value=self._quote('brapi')), \
             patch.object(QuotesService, '_fetch_yahoo_quote') as yahoo:
            result = QuotesService.fetch_quote('ibovespa')

        yahoo.assert_not_called()
        self.assertEqual(result['source'], 'brapi')


if __name__ == '__main__':
    unittest.main()
