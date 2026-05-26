"""
News Service - Fetches news from RSS feeds
Supports BBC Brasil, CNN Brasil, Bloomberg, Jovem Pan, Agência Brasil, etc.
"""

import feedparser
import requests
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Dict, Optional
from ..utils.logger import get_logger

logger = get_logger('mirofish.services.news')

class NewsService:
    """Service to fetch news from RSS feeds"""
    
    # RSS Feed URLs for Brazilian and international sources
    NEWS_SOURCES = {
        'bbc_brasil': {
            'url': 'https://feeds.bbci.co.uk/portuguese/rss.xml',
            'name': 'BBC Brasil',
            'language': 'pt-BR'
        },
        'cnn_brasil': {
            'url': 'https://www.cnnbrasil.com.br/feed/',
            'name': 'CNN Brasil',
            'language': 'pt-BR'
        },
        'bloomberg': {
            'url': 'https://feeds.bloomberg.com/markets/news.rss',
            'name': 'Bloomberg News',
            'language': 'en'
        },
        'jovem_pan': {
            'url': 'https://jovempan.com.br/feed/',
            'name': 'Jovem Pan News',
            'language': 'pt-BR'
        },
        'agencia_brasil': {
            'url': 'https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml',
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
        }
    }

    @staticmethod
    def _parse_feed(url: str):
        """Fetch and parse RSS with headers to avoid common 403/empty responses."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MiroFish/1.0; +https://github.com/Trustcorporation88/future-fish)'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return feedparser.parse(response.content)
        except Exception as e:
            logger.warning(f"Direct RSS request failed for {url}: {str(e)}; trying feedparser directly")
            return feedparser.parse(url)

    @staticmethod
    def _entry_datetime(entry) -> datetime:
        """Parse feed entry published date from multiple RSS/Atom formats."""
        parsed_time = entry.get('published_parsed') or entry.get('updated_parsed')
        if parsed_time:
            return datetime(*parsed_time[:6])

        date_text = entry.get('published') or entry.get('updated') or ''
        if date_text:
            try:
                return parsedate_to_datetime(date_text).replace(tzinfo=None)
            except Exception:
                try:
                    return datetime.fromisoformat(date_text.replace('Z', '+00:00')).replace(tzinfo=None)
                except Exception:
                    pass

        return datetime.now()

    @staticmethod
    def _article_from_entry(entry, source_key: str, source_info: Dict, category: str = 'general') -> Dict:
        published_at = NewsService._entry_datetime(entry)
        return {
            'source': source_info['name'],
            'source_key': source_key,
            'title': entry.get('title', 'Sem título'),
            'link': entry.get('link', ''),
            'summary': entry.get('summary', entry.get('description', ''))[:300],
            'published': published_at.isoformat(),
            'published_ts': published_at.timestamp(),
            'language': source_info['language'],
            'category': category
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
                feed = NewsService._parse_feed(source_info['url'])
                
                if getattr(feed, 'bozo', False):
                    logger.warning(f"Feed parsing warning for {source_info['name']}: {feed.bozo_exception}")
                
                for entry in feed.entries[:limit]:
                    articles.append(NewsService._article_from_entry(entry, source_key, source_info))
                    
            except Exception as e:
                logger.error(f"Error fetching news from {source_info['name']}: {str(e)}")
                continue
        
        # Sort by published date (most recent first)
        articles.sort(key=lambda x: x.get('published_ts', 0), reverse=True)
        
        return articles[:limit * len(sources_to_fetch) if not source else limit]
    
    @staticmethod
    def fetch_market_news(limit: int = 10) -> List[Dict]:
        """Fetch only market/financial news"""
        market_sources = NewsService.NEWS_SOURCES
        
        articles = []
        for source_key, source_info in market_sources.items():
            try:
                feed = NewsService._parse_feed(source_info['url'])
                
                for entry in feed.entries[:limit]:
                    articles.append(NewsService._article_from_entry(entry, source_key, source_info, category='market'))
                    
            except Exception as e:
                logger.error(f"Error fetching market news from {source_info['name']}: {str(e)}")
                continue
        
        articles.sort(key=lambda x: x.get('published_ts', 0), reverse=True)
        
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
