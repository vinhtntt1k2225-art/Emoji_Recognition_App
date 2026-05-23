"""
Pydantic models / schemas for API requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# Auth schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Prediction schemas
class PredictRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded canvas image")


class PredictionResult(BaseModel):
    class_id: int
    name: str
    emoji: str
    label: str
    confidence: float


class PredictResponse(BaseModel):
    success: bool
    predictions: List[PredictionResult]


# History schemas
class HistoryItem(BaseModel):
    id: int
    predicted_emoji: str
    predicted_label: str
    confidence: float
    top_predictions: Optional[str] = None
    created_at: Optional[str] = None


class HistoryResponse(BaseModel):
    predictions: List[HistoryItem]
    total: int


# Category schemas
class CategoryItem(BaseModel):
    id: int
    name: str
    emoji: str
    label: str


class CategoriesResponse(BaseModel):
    categories: List[CategoryItem]
    total: int
