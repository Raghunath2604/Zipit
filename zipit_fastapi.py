from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import hashlib
import json
from datetime import datetime
import uvicorn

app = FastAPI(title="ZipIt MLOps Platform")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
def init_db():
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, 
                  password_hash TEXT, tier TEXT DEFAULT 'free', created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS models
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, 
                  type TEXT, framework TEXT, created_at TEXT)''')
    
    # Admin user
    admin_hash = hashlib.sha256("zip@2604".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, email, password_hash, tier) VALUES (?, ?, ?, ?)",
              ("admin", "admin@zipit.com", admin_hash, "elite"))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Tier limits
TIER_LIMITS = {
    'free': {'models': 3, 'storage': '1 GB', 'price': 'Free'},
    'developer': {'models': 15, 'storage': '25 GB', 'price': '$15/3mo'},
    'elite': {'models': 100, 'storage': '500 GB', 'price': '$55/year'}
}

# Session management (simple in-memory for demo)
sessions = {}

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None

def authenticate(username: str, password: str):
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    user = c.fetchone()
    conn.close()
    return user

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard")
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate(username, password)
    if user:
        session_id = hashlib.md5(f"{user[1]}{datetime.now()}".encode()).hexdigest()
        sessions[session_id] = {
            'id': user[0], 'username': user[1], 'email': user[2], 'tier': user[4]
        }
        response = RedirectResponse("/dashboard", status_code=302)
        response.set_cookie("session_id", session_id)
        return response
    
    return templates.TemplateResponse("login.html", {
        "request": request, "error": "Invalid credentials"
    })

@app.post("/register")
async def register(request: Request, username: str = Form(...), 
                  email: str = Form(...), password: str = Form(...)):
    if len(password) < 8:
        return templates.TemplateResponse("login.html", {
            "request": request, "error": "Password must be at least 8 characters"
        })
    
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        c.execute("INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                  (username, email, password_hash, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return templates.TemplateResponse("login.html", {
            "request": request, "success": "Registration successful! Please login."
        })
    except:
        conn.close()
        return templates.TemplateResponse("login.html", {
            "request": request, "error": "Username or email already exists"
        })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/")
    
    # Get user's models
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    c.execute("SELECT * FROM models WHERE user_id=?", (user['id'],))
    models = c.fetchall()
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "models": models,
        "tier_limits": TIER_LIMITS[user['tier']]
    })

@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/")
    
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    c.execute("SELECT * FROM models WHERE user_id=?", (user['id'],))
    models = c.fetchall()
    conn.close()
    
    return templates.TemplateResponse("models.html", {
        "request": request, 
        "user": user, 
        "models": models,
        "tier_limits": TIER_LIMITS[user['tier']]
    })

@app.post("/upload_model")
async def upload_model(request: Request, model_name: str = Form(...), 
                      model_type: str = Form(...), framework: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/")
    
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    c.execute("INSERT INTO models (user_id, name, type, framework, created_at) VALUES (?, ?, ?, ?, ?)",
              (user['id'], model_name, model_type, framework, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return RedirectResponse("/models")

@app.get("/subscription", response_class=HTMLResponse)
async def subscription_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/")
    
    return templates.TemplateResponse("subscription.html", {
        "request": request, 
        "user": user,
        "tier_limits": TIER_LIMITS
    })

@app.post("/upgrade")
async def upgrade_subscription(request: Request, tier: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/")
    
    return templates.TemplateResponse("payment.html", {
        "request": request, 
        "user": user,
        "tier": tier,
        "price": TIER_LIMITS[tier]['price']
    })

@app.post("/process_payment")
async def process_payment(request: Request, tier: str = Form(...), 
                         transaction_id: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/")
    
    if transaction_id:
        # Update user tier
        conn = sqlite3.connect('zipit.db')
        c = conn.cursor()
        c.execute("UPDATE users SET tier=? WHERE id=?", (tier, user['id']))
        conn.commit()
        conn.close()
        
        # Update session
        sessions[request.cookies.get("session_id")]['tier'] = tier
        
        return templates.TemplateResponse("success.html", {
            "request": request, 
            "message": "Payment verified! Subscription upgraded."
        })
    
    return RedirectResponse("/subscription")

@app.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    
    response = RedirectResponse("/")
    response.delete_cookie("session_id")
    return response

# API endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "platform": "ZipIt MLOps"}

@app.get("/api/user")
async def get_user_info(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)