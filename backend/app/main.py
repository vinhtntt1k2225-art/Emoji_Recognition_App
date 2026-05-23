"""
Emoji Recognizer - FastAPI Backend

Main application with all API routes.
"""

import json
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .auth import hash_password, verify_password, create_access_token, decode_access_token
from .database import init_db, create_user, get_user_by_username, get_user_by_id, save_prediction, get_user_predictions
from .models import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    PredictRequest, PredictResponse, PredictionResult,
    HistoryResponse, HistoryItem, CategoriesResponse, CategoryItem,
)
from .ml.model import EMOJI_CLASSES
from .ml.predict import get_predictor


# Initialize FastAPI app
app = FastAPI(
    title="Emoji Recognizer API",
    description="AI-powered emoji recognition from hand-drawn sketches",
    version="1.0.0",
)

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    # Pre-load the model
    predictor = get_predictor()
    if predictor.is_ready:
        print("[OK] Emoji ANN model loaded and ready")
    else:
        print("[WARN] Model not loaded - run train.py first")


# ============================================================
# Auth helper
# ============================================================
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract current user from JWT token in Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Support both "Bearer <token>" and raw token
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# ============================================================
# Auth Routes
# ============================================================
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(data: UserRegister):
    """Register a new user."""
    # Check if user exists
    existing = get_user_by_username(data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    try:
        hashed_pw = hash_password(data.password)
        user = create_user(data.username, data.email, hashed_pw)
        
        token = create_access_token({"sub": str(user["id"])})
        
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                created_at=str(user.get("created_at", "")),
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login and get JWT token."""
    user = get_user_by_username(data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token({"sub": str(user["id"])})
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=str(user.get("created_at", "")),
        )
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=str(user.get("created_at", "")),
    )


# ============================================================
# Prediction Routes
# ============================================================
@app.post("/api/predict", response_model=PredictResponse)
async def predict_emoji(data: PredictRequest, user=Depends(get_current_user)):
    """Predict emoji from canvas drawing."""
    predictor = get_predictor()
    
    if not predictor.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first."
        )
    
    try:
        predictions = predictor.predict(data.image, top_k=3)
        
        # Save to history
        if predictions and predictions[0]["class_id"] >= 0:
            save_prediction(
                user_id=user["id"],
                emoji=predictions[0]["emoji"],
                label=predictions[0]["label"],
                confidence=predictions[0]["confidence"],
                top_predictions=json.dumps(predictions),
            )
        
        return PredictResponse(
            success=True,
            predictions=[PredictionResult(**p) for p in predictions],
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ============================================================
# History Routes
# ============================================================
@app.get("/api/history", response_model=HistoryResponse)
async def get_history(user=Depends(get_current_user)):
    """Get prediction history for current user."""
    predictions = get_user_predictions(user["id"])
    
    return HistoryResponse(
        predictions=[HistoryItem(
            id=p["id"],
            predicted_emoji=p["predicted_emoji"],
            predicted_label=p["predicted_label"],
            confidence=p["confidence"],
            top_predictions=p.get("top_predictions"),
            created_at=str(p.get("created_at", "")),
        ) for p in predictions],
        total=len(predictions),
    )


# ============================================================
# Categories Route
# ============================================================
@app.get("/api/categories", response_model=CategoriesResponse)
async def get_categories():
    """Get list of supported emoji categories."""
    return CategoriesResponse(
        categories=[CategoryItem(
            id=c["id"],
            name=c["name"],
            emoji=c["emoji"],
            label=c["label"],
        ) for c in EMOJI_CLASSES],
        total=len(EMOJI_CLASSES),
    )


# ============================================================
# Health Check
# ============================================================
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    predictor = get_predictor()
    return {
        "status": "healthy",
        "model_loaded": predictor.is_ready,
        "num_classes": len(EMOJI_CLASSES),
    }
