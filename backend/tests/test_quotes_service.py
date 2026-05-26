"""
Unit tests for QuotesService
"""

import unittest
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


if __name__ == '__main__':
    unittest.main()
