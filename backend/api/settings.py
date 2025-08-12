from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from services.settings_service import SettingsService

router = APIRouter()

# Models
class Settings(BaseModel):
    general: Dict[str, Any]
    appearance: Dict[str, Any]
    ai: Dict[str, Any]
    notifications: Dict[str, Any]

class UpdateSettingsRequest(BaseModel):
    category: str
    settings: Dict[str, Any]

# Initialize settings
SettingsService.initialize_settings()

@router.get("/")
async def get_settings():
    """Get all settings"""
    return SettingsService.get_all_settings()

@router.get("/{category}")
async def get_settings_category(category: str):
    """Get settings for a specific category"""
    settings = SettingsService.get_category_settings(category)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings category not found")
    return settings

@router.put("/")
async def update_settings(request: UpdateSettingsRequest):
    """Update settings for a category"""
    success = SettingsService.update_category_settings(request.category, request.settings)
    if not success:
        raise HTTPException(status_code=404, detail="Settings category not found")
    return {"message": "Settings updated successfully"}

@router.post("/reset")
async def reset_settings():
    """Reset all settings to default"""
    settings = SettingsService.reset_settings()
    return {"message": "Settings reset to default", "settings": settings}