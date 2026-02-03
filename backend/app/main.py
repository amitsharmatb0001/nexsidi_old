"""
MAIN APPLICATION FILE
=====================
This is the entry point of your entire backend.

Think of this as the "manager" of your restaurant:
- Sets up the building (FastAPI app)
- Hires the staff (routers for auth, projects, chat)
- Opens the doors (CORS, allows frontend to connect)
- Handles general operations (health checks, startup/shutdown)

When you run: uvicorn app.main:app --reload
This file is what actually runs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, projects, chat  # IMPORTANT: Added 'chat' here
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads DATABASE_URL, JWT_SECRET, API keys, etc.
load_dotenv()

# Create FastAPI application
# This is like constructing the restaurant building
app = FastAPI(
    title="NexSidi API",
    description="AI-powered software development platform - Build apps through conversation",
    version="1.0.0",
    docs_url="/docs",  # Interactive API documentation at http://localhost:8000/docs
    redoc_url="/redoc"  # Alternative documentation at http://localhost:8000/redoc
)

# CORS Configuration
# ==================
# CORS = Cross-Origin Resource Sharing
# 
# Non-technical explanation:
# Your frontend (React) runs on http://localhost:3000
# Your backend (FastAPI) runs on http://localhost:8000
# By default, browsers block frontend from talking to backend (security feature)
# CORS settings tell browser "it's okay, they're allowed to talk"
#
# Think of it like building security:
# - Frontend is a person trying to enter
# - Backend is the building
# - CORS is the access list saying "these people are allowed in"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default dev server
        "http://localhost:5173",  # Vite default dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,  # Allow cookies/authentication
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include Routers
# ===============
# Routers are like departments in your restaurant:
# - Auth router: Handles signups, logins (reception desk)
# - Projects router: Manages project data (order management)
# - Chat router: Handles conversations with Tilotma (the dining area)

app.include_router(
    auth.router, 
    prefix="/api/auth", 
    tags=["Authentication"]
)
# This creates endpoints:
# - POST /api/auth/signup
# - POST /api/auth/login
# - GET /api/auth/me

app.include_router(
    projects.router, 
    prefix="/api/projects", 
    tags=["Projects"]
)
# This creates endpoints:
# - POST /api/projects (create project)
# - GET /api/projects (list all projects)
# - GET /api/projects/{id} (get one project)
# - DELETE /api/projects/{id} (delete project)

app.include_router(
    chat.router, 
    prefix="/api/chat", 
    tags=["Chat"]
)
# This creates endpoints:
# - POST /api/chat/send (send message to Tilotma)
# - GET /api/chat/history (get conversation history)
# - DELETE /api/chat/history/{id} (delete one message)
# - POST /api/chat/clear (clear all messages)


# Root Endpoint
# =============
# When someone visits http://localhost:8000/ they see this
@app.get("/")
async def root():
    """
    Basic welcome message
    
    This is useful for:
    - Checking if server is running
    - Quick health check
    - Showing API info
    """
    return {
        "message": "Welcome to NexSidi API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",  # Link to interactive API documentation
        "description": "AI-powered software development platform"
    }


# Health Check Endpoint
# ======================
# Used by monitoring tools to check if server is alive
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Used by:
    - Load balancers (in production)
    - Monitoring services (UptimeRobot, Pingdom, etc.)
    - Deployment platforms (Railway, Vercel)
    - Your own monitoring scripts
    
    Returns:
    - status: "healthy" if everything working
    - database: "connected" (could ping database here in production)
    """
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2025-12-31T00:00:00Z"  # Could add real timestamp
    }


# Startup Event
# =============
# Runs once when server starts
@app.on_event("startup")
async def startup_event():
    """
    Things to do when application starts
    
    Current: Just print status messages
    Future possibilities:
    - Initialize database connection pool
    - Warm up AI model caches
    - Load configuration
    - Start background tasks
    - Register with service discovery
    """
    print("=" * 60)
    print("🚀 NexSidi API Starting Up...")
    print("=" * 60)
    print(f"📊 Database: {os.getenv('DATABASE_URL', 'Not configured')[:50]}...")
    print(f"🔐 JWT Secret: {'Configured' if os.getenv('JWT_SECRET') else 'Using default (NOT SECURE!)'}")
    print(f"🤖 Anthropic API: {'Configured' if os.getenv('ANTHROPIC_API_KEY') else 'Not configured'}")
    print(f"🤖 Google API: {'Configured' if os.getenv('GOOGLE_API_KEY') else 'Not configured'}")
    print("=" * 60)
    print("✅ Server Ready!")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("💬 Chat Endpoint: http://localhost:8000/api/chat/send")
    print("=" * 60)


# Shutdown Event
# ==============
# Runs once when server stops (Ctrl+C pressed)
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup when application shuts down
    
    Current: Just print message
    Future possibilities:
    - Close database connections
    - Finish pending tasks
    - Save state
    - Notify monitoring services
    """
    print("\n" + "=" * 60)
    print("👋 NexSidi API Shutting Down...")
    print("=" * 60)


# Development Server
# ==================
# When you run: python app/main.py
# This section runs (but normally you use uvicorn command instead)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True  # Auto-restart when code changes (DEVELOPMENT ONLY!)
    )