from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import uvicorn
import time

from api import chat, library, task, task_template, settings, websocket, agent, webcrawl
from utils.logger import api_logger

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="MAKOTO Visual API", version="1.0.0")

# ミドルウェアで全リクエストをログ
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # リクエスト情報をログ
    api_logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    # リクエストを処理
    response = await call_next(request)
    
    # レスポンス時間を計算
    process_time = time.time() - start_time
    api_logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if not os.path.exists("uploads"):
    os.makedirs("uploads")
if not os.path.exists("uploads/generated_images"):
    os.makedirs("uploads/generated_images")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(library.router, prefix="/api/library", tags=["library"])
app.include_router(task.router, prefix="/api/tasks", tags=["task"])
app.include_router(task_template.router, prefix="/api", tags=["task_template"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(webcrawl.router, prefix="/api/webcrawl", tags=["webcrawl"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "MAKOTO Visual API", "version": "1.0.0"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, reload=True)