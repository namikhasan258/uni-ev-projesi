# main.py
import os
import sys

# Set default environment variables before any imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./uniev.db")
os.environ.setdefault("JWT_SECRET", "default-secret-change-in-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_DAYS", "7")

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
        print("✓ Loaded .env file")
    else:
        print("⚠ No .env file found, using defaults")
except ImportError:
    print("⚠ python-dotenv not installed, using defaults")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from jinja2 import Environment, FileSystemLoader
import socketio

try:
    from database import create_tables
    from sockets.events import sio
    from routers import (
        auth, listings, messages, match, reports, 
        favorites, notifications, privacy, safety, 
        upload, users, admin, ratings
    )
    IMPORTS_OK = True
except Exception as e:
    print(f"⚠ Warning: Some imports failed: {e}")
    IMPORTS_OK = False

# Create FastAPI app
app = FastAPI(title="UniEv API", version="2.0.0")

# CORS configuration
origins = [
    os.getenv("CORS_ORIGIN", "http://localhost:3000"),
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory before mounting
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

# Register routers only if imports succeeded
if IMPORTS_OK:
    app.include_router(auth.router)
    app.include_router(listings.router)
    app.include_router(messages.router)
    app.include_router(match.router)
    app.include_router(reports.router)
    app.include_router(ratings.router)
    app.include_router(favorites.router)
    app.include_router(notifications.router)
    app.include_router(privacy.router)
    app.include_router(safety.router)
    app.include_router(upload.router)
    app.include_router(users.router)
    app.include_router(admin.router)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates - disable caching to fix Python 3.14 compatibility issue
jinja_env = Environment(loader=FileSystemLoader("templates"), auto_reload=True, cache_size=0)
templates = Jinja2Templates(env=jinja_env)

# Mount Socket.IO only if imports succeeded
if IMPORTS_OK:
    socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
else:
    socket_app = app


# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.get("/verify-success", response_class=HTMLResponse)
async def verify_success_page(request: Request):
    """Email verification success page"""
    return templates.TemplateResponse(request=request, name="verify-success.html")


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """Password reset page (accessed via email link)"""
    return templates.TemplateResponse(request=request, name="reset-password.html")


@app.get("/listings", response_class=HTMLResponse)
async def listings_page(request: Request):
    return templates.TemplateResponse(request=request, name="listings.html")


@app.get("/listing/{listing_id}", response_class=HTMLResponse)
async def listing_detail_page(request: Request, listing_id: str):
    return templates.TemplateResponse(request=request, name="listing_detail.html", context={"listing_id": listing_id})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html")


@app.get("/profile-debug", response_class=HTMLResponse)
async def profile_debug_page(request: Request):
    return templates.TemplateResponse(request=request, name="profile_debug.html")


@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    # Let JavaScript handle authentication check
    return templates.TemplateResponse(request=request, name="messages.html")


@app.get("/match", response_class=HTMLResponse)
async def match_page(request: Request):
    return templates.TemplateResponse(request=request, name="match.html")


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return templates.TemplateResponse(request=request, name="help.html")


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def user_profile_page(request: Request, user_id: str):
    return templates.TemplateResponse(request=request, name="user_profile.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin_dashboard.html")


@app.get("/create-listing", response_class=HTMLResponse)
async def create_listing_page(request: Request):
    return templates.TemplateResponse(request=request, name="create_listing.html")


@app.get("/edit-listing/{listing_id}", response_class=HTMLResponse)
async def edit_listing_page(request: Request, listing_id: str):
    return templates.TemplateResponse(request=request, name="edit_listing.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin/dashboard.html")


# Startup event
@app.on_event("startup")
async def startup():
    try:
        if IMPORTS_OK:
            create_tables()
            print("✅ UniEv API started. Database tables created.")
        else:
            print("⚠ UniEv API started in limited mode (some features disabled)")
    except Exception as e:
        print(f"⚠ Error during startup: {e}")
        import traceback
        traceback.print_exc()


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "imports": "ok" if IMPORTS_OK else "partial",
        "message": "UniEv API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    import os
    favicon_path = "static/images/Logo.png"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        raise HTTPException(404, "Favicon not found")


# For running: uvicorn main:socket_app --host 0.0.0.0 --port 8000


# Run the server
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting UniEv server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("⏹️  Press CTRL+C to stop the server")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
