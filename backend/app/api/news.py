"""
News API Routes
Provides endpoints for fetching news from various sources
"""

import traceback
from datetime import datetime
from flask import request, jsonify, Blueprint
from ..services.news_service import NewsService
from ..services.quotes_service import QuotesService
from ..utils.logger import get_logger
from ..utils.locale import t

logger = get_logger('mirofish.api.news')

# Create blueprints
news_bp = Blueprint('news', __name__, url_prefix='/api/news')
quotes_bp = Blueprint('quotes', __name__, url_prefix='/api/quotes')


@news_bp.route('/list', methods=['GET'])
def list_news():
    """
    Get latest news from configured sources
    
    Query Parameters:
        source: Specific source key (optional)
        limit: Maximum number of articles (default: 10)
        category: News category - 'market', 'general', 'international' (default: 'general')
    
    Returns:
        {
            "success": true,
            "data": {
                "articles": [
                    {
                        "source": "BBC Brasil",
                        "title": "...",
                        "link": "...",
                        "summary": "...",
                        "published": "2025-12-13T...",
                        "language": "pt-BR"
                    },
                    ...
                ],
                "count": 10,
                "sources_available": ["BBC Brasil", "CNN Brasil", ...]
            }
        }
    """
    try:
        source = request.args.get('source')
        limit = request.args.get('limit', 10, type=int)
        category = request.args.get('category', 'general')
        
        # Validate limit
        limit = min(max(limit, 1), 50)  # Between 1 and 50
        
        # Fetch news based on category
        if category == 'market':
            articles = NewsService.fetch_market_news(limit=limit)
        else:
            articles = NewsService.fetch_news(source=source, limit=limit)
        
        sources_available = list(NewsService.NEWS_SOURCES.keys())
        
        return jsonify({
            "success": True,
            "data": {
                "articles": articles,
                "count": len(articles),
                "sources_available": sources_available,
                "category": category
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@news_bp.route('/sources', methods=['GET'])
def get_news_sources():
    """
    Get list of available news sources
    
    Returns:
        {
            "success": true,
            "data": {
                "sources": [
                    {
                        "key": "bbc_brasil",
                        "name": "BBC Brasil",
                        "language": "pt-BR"
                    },
                    ...
                ],
                "count": 8
            }
        }
    """
    try:
        sources = [
            {
                "key": key,
                "name": info['name'],
                "language": info['language']
            }
            for key, info in NewsService.NEWS_SOURCES.items()
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "sources": sources,
                "count": len(sources)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting news sources: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@news_bp.route('/market', methods=['GET'])
def get_market_news():
    """
    Get market/financial news
    
    Query Parameters:
        limit: Maximum number of articles (default: 10)
    
    Returns:
        {
            "success": true,
            "data": {
                "articles": [...],
                "count": 10,
                "category": "market"
            }
        }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(max(limit, 1), 50)
        
        articles = NewsService.fetch_market_news(limit=limit)
        
        return jsonify({
            "success": True,
            "data": {
                "articles": articles,
                "count": len(articles),
                "category": "market"
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching market news: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@news_bp.route('/search', methods=['POST'])
def search_news():
    """
    Search news (placeholder for future implementation)
    
    Request (JSON):
        {
            "query": "search term",
            "limit": 10
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Query parameter is required"
            }), 400
        
        # For now, just return all news and client can filter
        # Future: implement actual search with keyword matching
        articles = NewsService.fetch_news(limit=limit)
        
        # Simple client-side filtering
        filtered = [
            a for a in articles
            if query.lower() in a['title'].lower() or query.lower() in a['summary'].lower()
        ]
        
        return jsonify({
            "success": True,
            "data": {
                "articles": filtered,
                "count": len(filtered),
                "query": query
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching news: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= QUOTES/PRICES ENDPOINTS =============

@quotes_bp.route('/list', methods=['GET'])
def list_quotes():
    """
    Get all available quotes (S&P 500, Dow Jones, IBOVESPA, Dólar, Petróleo Brent, Ouro, Bitcoin)
    
    Returns:
        {
            "success": true,
            "data": {
                "quotes": [
                    {
                        "key": "sp500",
                        "name": "S&P 500",
                        "price": 5123.45,
                        "change": 45.67,
                        "change_percent": 0.90,
                        "currency": "USD",
                        "timestamp": "2025-12-13T..."
                    },
                    ...
                ],
                "count": 7,
                "timestamp": "2025-12-13T..."
            }
        }
    """
    try:
        quotes = QuotesService.fetch_all_quotes()
        
        return jsonify({
            "success": True,
            "data": {
                "quotes": quotes,
                "count": len(quotes),
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error fetching quotes: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@quotes_bp.route('/<quote_key>', methods=['GET'])
def get_quote(quote_key: str):
    """
    Get a specific quote by key
    
    Keys available:
        - sp500 (S&P 500)
        - dowjones (Dow Jones)
        - ibovespa (IBOVESPA)
        - dolar (Dólar/Real)
        - brent (Petróleo Brent)
        - ouro (Ouro)
        - bitcoin (Bitcoin)
    
    Returns:
        {
            "success": true,
            "data": {
                "key": "sp500",
                "name": "S&P 500",
                "price": 5123.45,
                "change": 45.67,
                "change_percent": 0.90,
                ...
            }
        }
    """
    try:
        quote = QuotesService.fetch_quote(quote_key)
        
        if not quote:
            return jsonify({
                "success": False,
                "error": f"Quote not found or API error: {quote_key}"
            }), 404
        
        return jsonify({
            "success": True,
            "data": quote
        })
    except Exception as e:
        logger.error(f"Error fetching quote {quote_key}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@quotes_bp.route('/available', methods=['GET'])
def get_available_quotes():
    """
    Get list of available quote symbols
    
    Returns:
        {
            "success": true,
            "data": {
                "quotes": [
                    {
                        "key": "sp500",
                        "name": "S&P 500",
                        "symbol": "^GSPC",
                        "type": "index",
                        "currency": "USD",
                        "source": "finnhub"
                    },
                    ...
                ],
                "count": 7
            }
        }
    """
    try:
        quotes = QuotesService.get_available_quotes()
        
        return jsonify({
            "success": True,
            "data": {
                "quotes": quotes,
                "count": len(quotes)
            }
        })
    except Exception as e:
        logger.error(f"Error getting available quotes: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
