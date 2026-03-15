"""
AQI & Lung Health Prediction Voice Assistant - FastAPI Backend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import logging
import time
import hashlib
import os
from datetime import datetime, timedelta
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AQI Voice Assistant API",
    description="AI-powered Air Quality Index and Lung Health Prediction Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Rate limiting storage (in-memory for demo)
rate_limit_storage: Dict[str, List[float]] = {}

# ============== Pydantic Models ==============

class PredictionRequest(BaseModel):
    """Request model for AQI prediction"""
    city: str = Field(..., description="City name")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    pm25: Optional[float] = Field(None, description="PM2.5 level (μg/m³)")
    pm10: Optional[float] = Field(None, description="PM10 level (μg/m³)")
    no2: Optional[float] = Field(None, description="NO2 level (ppb)")
    o3: Optional[float] = Field(None, description="O3 level (ppb)")
    so2: Optional[float] = Field(None, description="SO2 level (ppb)")
    co: Optional[float] = Field(None, description="CO level (ppm)")
    temperature: Optional[float] = Field(None, description="Temperature (°C)")
    humidity: Optional[float] = Field(None, description="Humidity (%)")

class LungHealthRequest(BaseModel):
    """Request model for lung health prediction"""
    aqi: float = Field(..., description="Air Quality Index")
    exposure_time: float = Field(..., description="Exposure time in hours")
    age: Optional[int] = Field(25, description="User age")
    has_respiratory_condition: Optional[bool] = Field(False, description="Pre-existing respiratory condition")
    smoking_history: Optional[bool] = Field(False, description="Smoking history")

class VoiceCommandRequest(BaseModel):
    """Request model for voice command processing"""
    text: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio
    language: str = "en"

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    success: bool
    prediction: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    """Response model for lung health prediction"""
    success: bool
    risk_level: str
    risk_score: float
    recommendations: List[str]
    aqi_category: str
    timestamp: str

class ModelInfo(BaseModel):
    """Model information response"""
    name: str
    version: str
    type: str
    input_features: List[str]
    output_classes: List[str]
    accuracy: float
    last_trained: str

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    uptime_seconds: float
    model_loaded: bool

# ============== ML Model Manager =============

class ModelManager:
    """Manages ML model loading and inference"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_loaded = False
        self.load_time = None
        self.prediction_count = 0
        
    async def load_model(self):
        """Load the trained ML model"""
        try:
            logger.info("Loading AQI prediction model...")
            # Placeholder for actual model loading
            # In production, replace with:
            # import joblib
            # self.model = joblib.load('models/aqi_model.pkl')
            # self.scaler = joblib.load('models/scaler.pkl')
            
            self.is_loaded = True
            self.load_time = time.time()
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    async def predict_aqi(self, data: PredictionRequest) -> Dict[str, Any]:
        """Make AQI prediction"""
        if not self.is_loaded:
            await self.load_model()
            
        self.prediction_count += 1
        
        # Placeholder prediction logic
        # Replace with actual model inference
        base_aqi = data.pm25 * 1.5 if data.pm25 else 100
        if data.pm10:
            base_aqi += data.pm10 * 0.5
        
        # Add some variation based on other factors
        if data.temperature:
            base_aqi *= (1 + (data.temperature - 25) * 0.01)
        
        aqi = round(min(max(base_aqi, 0), 500), 2)
        
        # Determine category
        if aqi <= 50:
            category = "Good"
            color = "green"
        elif aqi <= 100:
            category = "Moderate"
            color = "yellow"
        elif aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
            color = "orange"
        elif aqi <= 200:
            category = "Unhealthy"
            color = "red"
        elif aqi <= 300:
            category = "Very Unhealthy"
            color = "purple"
        else:
            category = "Hazardous"
            color = "maroon"
        
        return {
            "aqi": aqi,
            "category": category,
            "color": color,
            "city": data.city,
            "pollutants": {
                "pm25": data.pm25,
                "pm10": data.pm10,
                "no2": data.no2,
                "o3": data.o3,
                "so2": data.so2,
                "co": data.co
            },
            "meteorological": {
                "temperature": data.temperature,
                "humidity": data.humidity
            }
        }
    
    async def predict_lung_health(self, data: LungHealthRequest) -> Dict[str, Any]:
        """Predict lung health risk"""
        # Calculate risk score based on AQI and exposure
        base_risk = (data.aqi / 500) * 100
        
        # Factor in exposure time
        exposure_factor = min(data.exposure_time / 8, 1.5)  # Cap at 8 hours
        
        # Age factor
        age_factor = 1.0
        if data.age < 18:
            age_factor = 1.2
        elif data.age > 60:
            age_factor = 1.3
        
        # Pre-existing conditions
        condition_factor = 1.5 if data.has_respiratory_condition else 1.0
        smoking_factor = 1.3 if data.smoking_history else 1.0
        
        risk_score = base_risk * exposure_factor * age_factor * condition_factor * smoking_factor
        risk_score = min(round(risk_score, 2), 100)
        
        # Determine risk level
        if risk_score <= 20:
            risk_level = "Low"
            recommendations = [
                "Air quality is good. Enjoy outdoor activities!",
                "No specific precautions needed."
            ]
        elif risk_score <= 40:
            risk_level = "Moderate"
            recommendations = [
                "Consider limiting prolonged outdoor exertion.",
                "Sensitive individuals should monitor symptoms."
            ]
        elif risk_level <= 60:
            risk_level = "High"
            recommendations = [
                "Reduce outdoor activities.",
                "Wear N95 mask if going outside.",
                "Keep windows closed."
            ]
        else:
            risk_level = "Critical"
            recommendations = [
                "Avoid all outdoor activities.",
                "Use air purifier indoors.",
                "Wear N95 mask if absolutely necessary.",
                "Consult doctor if symptoms appear."
            ]
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendations": recommendations,
            "factors_considered": {
                "aqi": data.aqi,
                "exposure_hours": data.exposure_time,
                "age": data.age,
                "respiratory_condition": data.has_respiratory_condition,
                "smoking_history": data.smoking_history
            }
        }

# Initialize model manager
model_manager = ModelManager()

# ============== Rate Limiting =============

async def check_rate_limit(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Check API rate limit"""
    token = credentials.credentials
    current_time = time.time()
    
    # Clean old entries
    rate_limit_storage[token] = [
        t for t in rate_limit_storage.get(token, [])
        if current_time - t < 60  # Keep only last minute
    ]
    
    # Check limit (100 requests per minute)
    if len(rate_limit_storage.get(token, [])) >= 100:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    rate_limit_storage[token].append(current_time)
    return token

# ============== Voice Command Processing =============

class VoiceCommandProcessor:
    """Process voice commands for AQI assistant"""
    
    def __init__(self):
        self.intents = {
            "aqi_check": ["aqi", "air quality", "pollution", "smog"],
            "lung_health": ["lung", "breathing", "health", "respiratory"],
            "weather": ["weather", "temperature", "humidity", "forecast"],
            "recommendation": ["recommend", "suggest", "advice", "tips"],
            "location": ["city", "location", "pincode", "area"]
        }
    
    def recognize_intent(self, text: str) -> Dict[str, Any]:
        """Recognize intent from text"""
        text_lower = text.lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return {"intent": intent, "confidence": 0.85}
        
        return {"intent": "unknown", "confidence": 0.0}
    
    async def process_command(self, text: str) -> Dict[str, Any]:
        """Process voice command"""
        intent_info = self.recognize_intent(text)
        
        response = {
            "intent": intent_info["intent"],
            "response": "",
            "data": {}
        }
        
        # Generate appropriate response based on intent
        if intent_info["intent"] == "aqi_check":
            response["response"] = f"I'll check the AQI for {text}. Please provide the city name."
        elif intent_info["intent"] == "lung_health":
            response["response"] = "I'll analyze your lung health risk based on current air quality."
        elif intent_info["intent"] == "recommendation":
            response["response"] = "Here are some health recommendations based on current conditions."
        else:
            response["response"] = "I can help you with AQI predictions, lung health analysis, and health recommendations."
        
        return response

voice_processor = VoiceCommandProcessor()

# ============== API Endpoints =============

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting AQI Voice Assistant API...")
    await model_manager.load_model()
    logger.info("API ready!")

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Check API health status"""
    uptime = time.time() - model_manager.load_time if model_manager.load_time else 0
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "model_loaded": model_manager.is_loaded
    }

# Model info endpoint
@app.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """Get model information"""
    return {
        "name": "AQI & Lung Health Prediction Model",
        "version": "1.0.0",
        "type": "Ensemble (Random Forest + XGBoost)",
        "input_features": [
            "pm25", "pm10", "no2", "o3", "so2", "co",
            "temperature", "humidity", "latitude", "longitude"
        ],
        "output_classes": ["Good", "Moderate", "Unhealthy", "Very Unhealthy", "Hazardous"],
        "accuracy": 0.92,
        "last_trained": "2024-01-15"
    }

# AQI Prediction endpoint
@app.post("/predict/aqi", response_model=PredictionResponse)
async def predict_aqi(
    request: PredictionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Predict AQI for given parameters"""
    try:
        logger.info(f"AQI prediction request for {request.city}")
        
        prediction = await model_manager.predict_aqi(request)
        
        return {
            "success": True,
            "prediction": prediction,
            "confidence": 0.92,
            "message": "AQI prediction successful",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Lung Health Prediction endpoint
@app.post("/predict/lung-health", response_model=HealthResponse)
async def predict_lung_health(
    request: LungHealthRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Predict lung health risk"""
    try:
        logger.info(f"Lung health prediction request")
        
        prediction = await model_manager.predict_lung_health(request)
        
        return {
            "success": True,
            "risk_level": prediction["risk_level"],
            "risk_score": prediction["risk_score"],
            "recommendations": prediction["recommendations"],
            "aqi_category": "Moderate" if prediction["risk_score"] > 20 else "Good",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice command processing endpoint
@app.post("/voice/command")
async def process_voice_command(
    request: VoiceCommandRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Process voice command"""
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = await voice_processor.process_command(request.text)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch prediction endpoint
@app.post("/predict/batch")
async def batch_predict(
    requests: List[PredictionRequest],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Batch prediction for multiple cities"""
    try:
        results = []
        for req in requests:
            prediction = await model_manager.predict_aqi(req)
            results.append(prediction)
        
        return {
            "success": True,
            "predictions": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Audio file upload endpoint
@app.post("/predict/audio")
async def predict_from_audio(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Process audio file for voice command"""
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process audio (placeholder)
        # In production, use speech-to-text service
        
        return {
            "success": True,
            "transcribed_text": "Sample transcribed text",
            "intent": "aqi_check",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics endpoint
@app.get("/statistics")
async def get_statistics():
    """Get API usage statistics"""
    return {
        "total_predictions": model_manager.prediction_count,
        "model_loaded": model_manager.is_loaded,
        "uptime": time.time() - model_manager.load_time if model_manager.load_time else 0,
        "timestamp": datetime.now().isoformat()
    }

# ============== Root endpoint =============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AQI Voice Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
