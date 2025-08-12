from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.library_service import LibraryService

router = APIRouter()

# Models
class LibraryItem(BaseModel):
    id: str
    name: str
    type: str  # folder, file
    parent_id: Optional[str] = None
    size: Optional[int] = None
    created_at: str
    updated_at: str
    path: str

class CreateFolderRequest(BaseModel):
    name: str
    parent_id: Optional[str] = None

# Initialize sample data
LibraryService.initialize_sample_data()

@router.get("/items")
async def get_library_items(parent_id: Optional[str] = None):
    """Get library items"""
    return LibraryService.get_items(parent_id)

@router.get("/items/{item_id}")
async def get_library_item(item_id: str):
    """Get a specific library item"""
    item = LibraryService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/folders")
async def create_folder(request: CreateFolderRequest):
    """Create a new folder"""
    folder = LibraryService.create_folder(request.name, request.parent_id)
    return folder

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), folder_id: Optional[str] = None):
    """Upload a file to library"""
    if folder_id:
        parent = LibraryService.get_item(folder_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    # Mock file save - In real implementation, save the file and get actual size
    file_item = LibraryService.create_file(
        name=file.filename,
        size=0,  # In real implementation, get actual file size
        parent_id=folder_id
    )
    
    return {"id": file_item['id'], "message": "File uploaded successfully"}

@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    """Delete a library item"""
    item = LibraryService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    LibraryService.delete_item(item_id)
    return {"message": "Item deleted successfully"}