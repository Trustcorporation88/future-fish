# Pull Request: Real-Time News & Market Quotes API

## Overview
This PR implements real-time news and market quotes functionality for the MiroFish prediction platform.

### Features Implemented

#### 1. News Service with RSS Feeds
- **Integrated News Sources:**
  - BBC Brasil
  - CNN Brasil
  - Bloomberg News
  - Jovem Pan News
  - Agência Brasil
  - Folha de S.Paulo (Mercado)
  - G1 (Economia)
  - Reuters (Markets)

- **API Endpoints:**
  - `GET /api/news/list` - Fetch latest news with optional filtering by source and category
  - `GET /api/news/market` - Financial/market news only
  - `GET /api/news/search` - Search news by query term
  - `GET /api/news/sources` - List all available news sources

#### 2. Market Quotes Service
- **Real-Time Quotes for:**
  - Stock Indices: S&P 500, Dow Jones, IBOVESPA
  - Currencies: USD/BRL (Dólar)
  - Commodities: Petróleo Brent, Ouro
  - Cryptocurrency: Bitcoin

- **API Endpoints:**
  - `GET /api/quotes/list` - All available quotes
  - `GET /api/quotes/{key}` - Specific quote (sp500, dowjones, ibovespa, dolar, brent, ouro, bitcoin)
  - `GET /api/quotes/available` - List all available quote symbols

#### 3. Data Sources
- **Finnhub API** - International stocks and commodities
- **BRAPI** - Brazilian market data (IBOVESPA, USD/BRL)
- **CoinGecko API** - Bitcoin and cryptocurrency data (free, no key required)

### Technical Implementation

#### New Files:
- `backend/app/services/news_service.py` - NewsService class for RSS feed fetching
- `backend/app/services/quotes_service.py` - QuotesService class for real-time quotes
- `backend/app/api/news.py` - Flask blueprints for news and quotes API endpoints
- `backend/tests/test_news_service.py` - Unit tests for NewsService
- `backend/tests/test_quotes_service.py` - Unit tests for QuotesService

#### Modified Files:
- `backend/app/__init__.py` - Register news_bp and quotes_bp blueprints
- `backend/requirements.txt` - Add feedparser and requests dependencies

### Testing
✅ All Python files pass syntax validation
✅ Frontend build completes without errors (689 modules, 1m 17s)
✅ Unit tests created for both services
✅ Service configuration validated

### Browser Integration
The feature branch `feat/url-and-file-formats` has been merged, adding:
- URL input support
- Multi-format file uploads (XLS, XLSX, JPG, JPEG, PNG, GIF, BMP, WEBP)
- Direct image paste from clipboard

### API Usage Examples

**Get all news:**
```bash
curl http://localhost:5001/api/news/list?limit=10&category=market
```

**Get S&P 500 quote:**
```bash
curl http://localhost:5001/api/quotes/sp500
```

**Get Bitcoin price:**
```bash
curl http://localhost:5001/api/quotes/bitcoin
```

### Related Issues
Closes the requirement for real-time news and market data in the prediction platform UI.

### Commits
- `a1efc6e` - test: Add unit tests for news and quotes services
- `adca3d6` - feat: Add news and quotes API endpoints with RSS feeds and real-time market data
- `f160742` - feat: Add URL links, expand file formats (XLS, JPG, PNG), and clipboard paste support

### How to Create the PR on GitHub

1. Go to: https://github.com/Trustcorporation88/future-fish
2. Click "Pull requests" tab
3. Click "New pull request"
4. Set:
   - Base: `main` (or any target branch)
   - Compare: `main` (the current branch with all commits)
5. Click "Create pull request"
6. Add the description from this file
7. Click "Create pull request"

### Verification Steps
1. Start the development server: `npm run dev`
2. Frontend should be at `http://localhost:3000`
3. Backend API at `http://localhost:5001`
4. Test endpoints:
   - `http://localhost:5001/api/news/list`
   - `http://localhost:5001/api/quotes/list`
   - `http://localhost:5001/api/quotes/bitcoin`

### Co-authors
Co-Authored-By: Oz <oz-agent@warp.dev>
