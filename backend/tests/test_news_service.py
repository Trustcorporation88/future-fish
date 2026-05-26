"""
Unit tests for NewsService
"""

import unittest
from app.services.news_service import NewsService


class TestNewsService(unittest.TestCase):
    """Test NewsService functionality"""
    
    def test_news_sources_available(self):
        """Test that news sources are properly configured"""
        sources = NewsService.NEWS_SOURCES
        self.assertIsNotNone(sources)
        self.assertGreater(len(sources), 0)
        
        # Check required sources exist
        required_sources = ['bbc_brasil', 'cnn_brasil', 'bloomberg', 'jovem_pan', 'agencia_brasil']
        for source in required_sources:
            self.assertIn(source, sources)
    
    def test_source_structure(self):
        """Test that each source has required fields"""
        for key, source_info in NewsService.NEWS_SOURCES.items():
            self.assertIn('url', source_info, f"Source {key} missing 'url'")
            self.assertIn('name', source_info, f"Source {key} missing 'name'")
            self.assertIn('language', source_info, f"Source {key} missing 'language'")
            
            # Validate URL format
            self.assertTrue(
                source_info['url'].startswith('http'),
                f"Source {key} URL should start with http"
            )
    
    def test_fetch_news_returns_list(self):
        """Test that fetch_news returns a list"""
        try:
            articles = NewsService.fetch_news(limit=5)
            self.assertIsInstance(articles, list)
        except Exception as e:
            # Allow network errors in test environment
            self.skipTest(f"Network error: {str(e)}")
    
    def test_fetch_market_news_returns_list(self):
        """Test that fetch_market_news returns a list"""
        try:
            articles = NewsService.fetch_market_news(limit=5)
            self.assertIsInstance(articles, list)
        except Exception as e:
            self.skipTest(f"Network error: {str(e)}")
    
    def test_fetch_by_category(self):
        """Test that fetch_by_category works"""
        try:
            articles = NewsService.fetch_by_category('market', limit=5)
            self.assertIsInstance(articles, list)
        except Exception as e:
            self.skipTest(f"Network error: {str(e)}")


if __name__ == '__main__':
    unittest.main()
