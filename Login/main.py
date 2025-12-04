"""
Stratego Swiss Knife - Main Application
Login system with dashboard for accessing multiple tools
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import sys

# Add parent directory to path for importing apps
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Stratego Swiss Knife")

# Session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key="stratego-swiss-knife-secret-2024")

# Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# ==================== AUTHENTICATION ====================

# Credenziali (in produzione usare database/hash)
VALID_CREDENTIALS = {
    "admin": "Stratego"
}

def get_current_user(request: Request):
    """Check if user is authenticated"""
    user = request.session.get("user")
    if not user:
        return None
    return user

def require_auth(request: Request):
    """Dependency to require authentication"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ==================== APPS REGISTRY ====================

APPS = [
    {
        "id": "seo_content_agent",
        "name": "SEO Content Agent",
        "description": "Genera contenuti SEO ottimizzati per e-commerce. Analizza keyword CSV, scraping prodotti e SERP.",
        "icon": "fas fa-search",
        "color": "#3b82f6",
        "url": "/app/seo",
        "status": "demo",
        "version": "v0.1.0"
    }
]

# Password per modifica versione 
VERSION_PASSWORD = "nicolas"


# ==================== ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Process login"""
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Credenziali non valide"
    })

@app.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard with apps list"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "apps": APPS
    })


# ==================== SEO APP INTEGRATION ====================

# L'app SEO gira su una porta separata
# Per ora usiamo redirect o embed

@app.get("/app/seo", response_class=HTMLResponse)
async def seo_app_redirect(request: Request):
    """Redirect to SEO app"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    # L'app SEO gira sulla porta 8001
    return templates.TemplateResponse("app_frame.html", {
        "request": request,
        "user": user,
        "app_url": "http://localhost:8001",
        "app_name": "SEO Content Agent"
    })


# ==================== API ====================

@app.get("/api/apps")
async def get_apps(user: str = Depends(require_auth)):
    """Get list of available apps"""
    return {"apps": APPS}

@app.get("/api/user")
async def get_user(request: Request):
    """Get current user info"""
    user = get_current_user(request)
    if user:
        return {"user": user, "authenticated": True}
    return {"user": None, "authenticated": False}


@app.post("/api/update-version")
async def update_version(
    request: Request,
    app_id: str = Form(...),
    version: str = Form(...),
    password: str = Form(...)
):
    """Update app version (password protected)"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if password != VERSION_PASSWORD:
        raise HTTPException(status_code=403, detail="Password errata")
    
    # Trova e aggiorna l'app
    for app_item in APPS:
        if app_item["id"] == app_id:
            app_item["version"] = version
            return {"success": True, "version": version}
    
    raise HTTPException(status_code=404, detail="App non trovata")


# ==================== MAIN ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
