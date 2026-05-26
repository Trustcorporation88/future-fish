"""
News Service - Fetches news from RSS feeds
Supports BBC Brasil, CNN Brasil, Bloomberg, Jovem Pan, Agência Brasil, etc.
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..utils.logger import get_logger

logger = get_logger('mirofish.services.news')

class NewsService:
    """Service to fetch news from RSS feeds"""
    
    # RSS Feed URLs for Brazilian and international sources
    NEWS_SOURCES = {
        'bbc_brasil': {
            'url': 'http://feeds.bbc.co.uk/mundo/rss.xml',
            'name': 'BBC Brasil',
            'language': 'pt-BR'
        },
        'cnn_brasil': {
            'url': 'https://www.cnnbrasil.com.br/feed/rss.xml',
            'name': 'CNN Brasil',
            'language': 'pt-BR'
        },
        'bloomberg': {
            'url': 'https://feeds.bloomberg.com/markets/news.rss',
            'name': 'Bloomberg News',
            'language': 'en'
        },
        'jovem_pan': {
            'url': 'https://www.jovempan.com.br/feed.xml',
            'name': 'Jovem Pan News',
            'language': 'pt-BR'
        },
        'agencia_brasil': {
            'url': 'https://agenciabrasil.ebc.com.br/feed.xml',
            'name': 'Agência Brasil',
            'language': 'pt-BR'
        },
        'folha': {
            'url': 'https://feeds.folha.uol.com.br/mercado/rss091.xml',
            'name': 'Folha de S.Paulo - Mercado',
            'language': 'pt-BR'
        },
        'g1_economia': {
            'url': 'https://g1.globo.com/rss/g1/economia/',
            'name': 'G1 - Economia',
            'language': 'pt-BR'
        },
        'reuters': {
            'url': 'https://www.reuters.com/finance/markets',
            'name': 'Reuters - Markets',
            'language': 'en'
        }
    }
    
    @staticmethod
    def fetch_news(source: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Fetch news from RSS feeds
        
        Args:
            source: Specific source key or None for all sources
            limit: Maximum number of articles per source
        
        Returns:
            List of news articles with title, link, published date, source
        """
        articles = []
        
        sources_to_fetch = {source: NewsService.NEWS_SOURCES[source]} if source else NewsService.NEWS_SOURCES
        
        for source_key, source_info in sources_to_fetch.items():
            try:
                logger.info(f"Fetching news from {source_info['name']}...")
                feed = feedparser.parse(source_info['url'])
                
                if feed.status != 200 and feed.bozo:
                    logger.warning(f"Feed parsing warning for {source_info['name']}: {feed.bozo_exception}")
                
                for entry in feed.entries[:limit]:
                    article = {
                        'source': source_info['name'],
                        'source_key': source_key,
                        'title': entry.get('title', 'N/A'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', '')[:300],  # First 300 chars
                        'published': entry.get('published', datetime.now().isoformat()),
                        'language': source_info['language']
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error fetching news from {source_info['name']}: {str(e)}")
                continue
        
        # Sort by published date (most recent first)
        articles.sort(
            key=lambda x: datetime.fromisoformat(x['published'].replace('Z', '+00:00')),
            reverse=True
        )
        
        return articles[:limit * len(sources_to_fetch) if not source else limit]
    
    @staticmethod
    def fetch_market_news(limit: int = 10) -> List[Dict]:
        """Fetch only market/financial news"""
        market_sources = {
            k: v for k, v in NewsService.NEWS_SOURCES.items()
            if any(keyword in k.lower() for keyword in ['folha', 'bloomberg', 'g1_economia'])
        }
        
        articles = []
        for source_key, source_info in market_sources.items():
            try:
                feed = feedparser.parse(source_info['url'])
                
                for entry in feed.entries[:limit]:
                    article = {
                        'source': source_info['name'],
                        'source_key': source_key,
                        'title': entry.get('title', 'N/A'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', '')[:300],
                        'published': entry.get('published', datetime.now().isoformat()),
                        'language': source_info['language'],
                        'category': 'market'
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error fetching market news from {source_info['name']}: {str(e)}")
                continue
        
        articles.sort(
            key=lambda x: datetime.fromisoformat(x['published'].replace('Z', '+00:00')),
            reverse=True
        )
        
        return articles[:limit]
    
    @staticmethod
    def fetch_by_category(category: str, limit: int = 10) -> List[Dict]:
        """
        Fetch news by category
        
        Args:
            category: 'market', 'technology', 'politics', 'general', 'international'
            limit: Maximum number of articles
        """
        if category == 'market':
            return NewsService.fetch_market_news(limit)
        
        # For other categories, fetch from all sources
        # (You can expand this to filter by keywords or dedicated RSS feeds)
        return NewsService.fetch_news(limit=limit)
