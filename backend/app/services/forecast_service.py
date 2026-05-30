"""
Forecast Service - Generates structured financial predictions
"""

import json
from typing import Dict, List, Optional, Any
from ..utils.llm_client import LLMClient
from ..utils.file_parser import FileParser
from ..services.news_service import NewsService
from ..services.quotes_service import QuotesService
from ..utils.logger import get_logger

logger = get_logger('mirofish.services.forecast')


class ForecastService:
    """Service to generate structured financial forecasts"""

    FORECAST_STRUCTURE = {
        "question": "str",
        "time_horizon": "str",
        "summary": "str",
        "direction": "str",  # 'bullish', 'bearish', 'neutral'
        "confidence": "float",  # 0-1
        "signals": ["str"],
        "risks": ["str"],
        "supporting_news": ["str"],
        "supporting_quotes": ["str"],
        "final_conclusion": "str"
    }

    @staticmethod
    def generate_forecast(
        question: str,
        time_horizon: str,
        context: Optional[str] = None,
        sources: Optional[List[str]] = None,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured forecast based on question, context, and market data.

        Args:
            question: The prediction question (e.g. "Will IBOVESPA rise?")
            time_horizon: Time frame (e.g. "24 hours", "1 week", "1 month")
            context: Additional context provided by user
            sources: List of URLs/sources mentioned
            files: List of file paths to extract text from

        Returns:
            Dictionary with structured forecast containing question, summary,
            direction, confidence, signals, risks, supporting_news, etc.
        """
        try:
            # 1. Fetch current market data
            logger.info(f"Fetching market data for forecast: {question}")
            quotes = QuotesService.fetch_all_quotes()
            news = NewsService.fetch_market_news(limit=8)

            # 2. Extract text from uploaded files
            file_context = ""
            if files:
                for file_path in files:
                    try:
                        text = FileParser.extract_text(file_path)
                        file_context += f"\n\n=== Documento ===\n{text}"
                    except Exception as e:
                        logger.warning(f"Error extracting from {file_path}: {str(e)}")

            # 3. Build the prompt
            prompt = ForecastService._build_prompt(
                question=question,
                time_horizon=time_horizon,
                context=context,
                sources=sources,
                quotes=quotes,
                news=news,
                file_context=file_context
            )

            # 4. Call LLM to generate forecast
            logger.info("Calling LLM to generate forecast")
            client = LLMClient()
            response = client.chat_json(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2048
            )

            # 5. Ensure response has required fields
            forecast = ForecastService._validate_forecast(response)
            forecast["question"] = question
            forecast["time_horizon"] = time_horizon

            logger.info(f"Forecast generated successfully for: {question}")
            return {
                "success": True,
                "data": forecast
            }

        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _build_prompt(
        question: str,
        time_horizon: str,
        context: Optional[str],
        sources: Optional[List[str]],
        quotes: List[Dict],
        news: List[Dict],
        file_context: str
    ) -> str:
        """Build the LLM prompt for forecast generation"""

        quotes_text = "\n".join([
            f"- {q['name']}: {q['price']} {q['currency']} ({q.get('change_percent', 0):+.2f}%)"
            for q in quotes
        ])

        news_text = "\n".join([
            f"- {n['source']}: {n['title']}"
            for n in news[:5]
        ])

        sources_text = ""
        if sources:
            sources_text = f"\n\nAdditional sources provided by user:\n" + "\n".join(
                [f"- {s}" for s in sources]
            )

        context_text = ""
        if context:
            context_text = f"\n\nUser's additional context:\n{context}"

        prompt = f"""You are a financial analyst. Based on the following information, generate a structured forecast for this question:

**Question:** {question}
**Time Horizon:** {time_horizon}

**Current Market Quotes:**
{quotes_text}

**Recent Market News:**
{news_text}{sources_text}{context_text}{file_context}

Generate a detailed forecast as JSON with these fields (all required):
- question: the original question
- time_horizon: the time frame
- summary: 2-3 sentence summary of your forecast
- direction: either 'bullish', 'bearish', or 'neutral'
- confidence: a number between 0 and 1 indicating your confidence (e.g., 0.75)
- signals: array of 3-5 key signals supporting your forecast
- risks: array of 3-5 key risks that could invalidate your forecast
- supporting_news: array of 2-3 news headlines that are relevant
- supporting_quotes: array of 2-3 market quotes (name and current price) that are relevant
- final_conclusion: a 1-2 sentence final recommendation

Respond ONLY with valid JSON."""

        return prompt

    @staticmethod
    def _validate_forecast(response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure forecast has all required fields"""
        forecast = {}

        # Required string fields
        for field in ["summary", "direction", "final_conclusion"]:
            forecast[field] = response.get(field, "")

        # Confidence as float
        confidence = response.get("confidence", 0.5)
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 0.5
        forecast["confidence"] = max(0.0, min(1.0, confidence))

        # Arrays
        forecast["signals"] = response.get("signals", [])
        if not isinstance(forecast["signals"], list):
            forecast["signals"] = []

        forecast["risks"] = response.get("risks", [])
        if not isinstance(forecast["risks"], list):
            forecast["risks"] = []

        forecast["supporting_news"] = response.get("supporting_news", [])
        if not isinstance(forecast["supporting_news"], list):
            forecast["supporting_news"] = []

        forecast["supporting_quotes"] = response.get("supporting_quotes", [])
        if not isinstance(forecast["supporting_quotes"], list):
            forecast["supporting_quotes"] = []

        return forecast
