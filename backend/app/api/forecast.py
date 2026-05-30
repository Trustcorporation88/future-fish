"""
Forecast API Routes - MVP endpoints for generating financial predictions
"""

import os
import json
import uuid
import traceback
from datetime import datetime
from flask import request, jsonify, Blueprint
from ..services.forecast_service import ForecastService
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.api.forecast')

# Create blueprint
forecast_bp = Blueprint('forecast', __name__, url_prefix='/api/forecast')

# Store forecasts in a simple dict (in production, use database)
forecasts = {}


@forecast_bp.route('/generate', methods=['POST'])
def generate_forecast():
    """
    Generate a forecast from question, context, and market data.
    
    Request (JSON or multipart/form-data):
        {
            "question": "Will IBOVESPA rise in the next 24 hours?",
            "time_horizon": "24 hours",
            "context": "Optional additional context...",
            "sources": ["https://example.com", "News source"],
            "files": [file uploads]
        }
    
    Response:
        {
            "success": true,
            "data": {
                "forecast_id": "fc_xxxx",
                "question": "...",
                "time_horizon": "...",
                "summary": "...",
                "direction": "bullish|bearish|neutral",
                "confidence": 0.75,
                "signals": [...],
                "risks": [...],
                "supporting_news": [...],
                "supporting_quotes": [...],
                "final_conclusion": "...",
                "created_at": "2025-12-13T..."
            }
        }
    """
    try:
        # Parse request
        question = request.form.get('question') or (request.get_json() or {}).get('question')
        time_horizon = request.form.get('time_horizon') or (request.get_json() or {}).get('time_horizon')
        context = request.form.get('context') or (request.get_json() or {}).get('context')
        sources = request.form.get('sources') or (request.get_json() or {}).get('sources', [])
        
        if not question or not time_horizon:
            return jsonify({
                "success": False,
                "error": "question and time_horizon are required"
            }), 400
        
        # Parse sources if it's a JSON string
        if isinstance(sources, str):
            try:
                sources = json.loads(sources)
            except (json.JSONDecodeError, TypeError):
                sources = []
        
        # Handle file uploads
        uploaded_files = request.files.getlist('files')
        file_paths = []
        
        uploads_dir = os.path.join(Config.UPLOAD_FOLDER, 'forecast_temp')
        os.makedirs(uploads_dir, exist_ok=True)
        
        for file in uploaded_files:
            if file and file.filename:
                # Save file temporarily
                filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
                filepath = os.path.join(uploads_dir, filename)
                file.save(filepath)
                file_paths.append(filepath)
        
        logger.info(f"Generating forecast: {question}")
        
        # Generate forecast
        result = ForecastService.generate_forecast(
            question=question,
            time_horizon=time_horizon,
            context=context,
            sources=sources,
            files=file_paths if file_paths else None
        )
        
        if not result.get("success"):
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to generate forecast")
            }), 500
        
        # Store forecast
        forecast_id = f"fc_{uuid.uuid4().hex[:12]}"
        forecast_data = result["data"]
        forecast_data["forecast_id"] = forecast_id
        forecast_data["created_at"] = datetime.now().isoformat()
        
        forecasts[forecast_id] = forecast_data
        
        # Clean up temporary files
        for fp in file_paths:
            try:
                os.remove(fp)
            except:
                pass
        
        return jsonify({
            "success": True,
            "data": forecast_data
        })
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@forecast_bp.route('/<forecast_id>', methods=['GET'])
def get_forecast(forecast_id: str):
    """
    Retrieve a forecast by ID.
    
    Response:
        {
            "success": true,
            "data": {
                "forecast_id": "fc_xxxx",
                "question": "...",
                ...all forecast fields...
            }
        }
    """
    if forecast_id not in forecasts:
        return jsonify({
            "success": False,
            "error": f"Forecast {forecast_id} not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": forecasts[forecast_id]
    })
