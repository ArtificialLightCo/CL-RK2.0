# app.py — CLÆRK 2.0 Main Backend (FastAPI)

import os
from fastapi import FastAPI, Request, Depends, HTTPException, status, Response, Cookie, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from fastapi.routing import APIRouter
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel, BaseSettings, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import stripe
import requests
import logging
import secrets

# ----- Settings -----
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./claerk.db"
    JWT_SECRET: str = "CHANGE_ME_SECRET"
    JWT_ALGO: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    BASE_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"
    CSRF_SECRET: str = "csrf-change-me"
    LLM_GATEWAY_URL: str = "http://localhost:9999/llm/generate"
    PSYCH_ENGINE_URL: str = "http://localhost:8001"
    ADMIN_EMAIL: str = "admin@example.com"
    EMAIL_API_KEY: str = ""  # (Optional: for future email features)
    RATE_LIMIT_PER_MIN: int = 60

settings = Settings()

# ----- Logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claerk")

# ----- CORS -----
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app = FastAPI(title="CLÆRK Storefront API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Templates -----
templates = Jinja2Templates(directory="frontend")

# ----- DB Setup -----
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

# ----- Password & Auth -----
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_pw(pw): return pwd_context.hash(pw)
def verify_pw(pw, hashed): return pwd_context.verify(pw, hashed)
def create_jwt(payload: dict, expires_delta=None):
    to_encode = payload.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + expires_delta})
    else:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)
def decode_jwt(token): return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])

# ----- Models -----
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    tags = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    stripe_session_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    product = relationship("Product")

Base.metadata.create_all(bind=engine)

# ----- API Routers -----
api_router = APIRouter()
admin_router = APIRouter()
product_router = APIRouter()
auth_router = APIRouter()
order_router = APIRouter()

# ----- Rate Limiting (simple per-IP memory store) -----
from collections import defaultdict
from time import time
rate_limit_memory = defaultdict(list)
def check_rate_limit(ip, max_per_min):
    now = time()
    hits = rate_limit_memory[ip]
    rate_limit_memory[ip] = [t for t in hits if now - t < 60]
    if len(rate_limit_memory[ip]) >= max_per_min:
        raise HTTPException(429, detail="Too many requests, slow down.")
    rate_limit_memory[ip].append(now)

# ----- CSRF Helper -----
def generate_csrf_token():
    return secrets.token_urlsafe(16)
def validate_csrf(csrf_cookie, csrf_form):
    return csrf_cookie and csrf_form and csrf_cookie == csrf_form

# ----- Dependency: DB session -----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Dependency: Get current user -----
def get_current_user(token: str = Cookie(None), db=Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing credentials")
    try:
        payload = decode_jwt(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(401, "Token missing subject")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ----- AUTH ROUTES -----
class RegisterForm(BaseModel):
    email: EmailStr
    password: str
class LoginForm(BaseModel):
    email: EmailStr
    password: str
class TokenOut(BaseModel):
    token: str

@auth_router.post("/register", response_model=TokenOut)
def register(form: RegisterForm, db=Depends(get_db)):
    existing = db.query(User).filter_by(email=form.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    user = User(email=form.email, hashed_password=hash_pw(form.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_jwt({"sub": user.email})
    return {"token": token}

@auth_router.post("/login", response_model=TokenOut)
def login(form: LoginForm, db=Depends(get_db)):
    user = db.query(User).filter_by(email=form.email).first()
    if not user or not verify_pw(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_jwt({"sub": user.email})
    return {"token": token}

@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"message": "Logged out"}

# ----- PRODUCT ROUTES -----
class ProductCreate(BaseModel):
    title: str
    slug: str
    description: str
    price: float
    category: str
    tags: str

@product_router.post("/", response_model=dict)
def create_product(prod: ProductCreate, db=Depends(get_db), user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admin only")
    p = Product(**prod.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"product": p.slug}

@product_router.get("/", response_model=list)
def list_products(db=Depends(get_db)):
    prods = db.query(Product).order_by(Product.created_at.desc()).all()
    return [{"title": p.title, "slug": p.slug, "price": p.price, "category": p.category, "tags": p.tags, "description": p.description} for p in prods]

@product_router.get("/{slug}", response_model=dict)
def get_product(slug: str, db=Depends(get_db)):
    p = db.query(Product).filter_by(slug=slug).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return {
        "title": p.title, "slug": p.slug, "price": p.price, "category": p.category,
        "tags": p.tags, "description": p.description
    }

# ----- ORDER/STRIPE ROUTES -----
stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutSessionIn(BaseModel):
    product_slug: str

@order_router.post("/checkout-session", response_model=dict)
def create_checkout_session(data: CheckoutSessionIn, db=Depends(get_db), user=Depends(get_current_user)):
    p = db.query(Product).filter_by(slug=data.product_slug).first()
    if not p:
        raise HTTPException(404, "Product not found")
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(p.price * 100),
                "product_data": {"name": p.title}
            },
            "quantity": 1
        }],
        mode="payment",
        customer_email=user.email,
        success_url=f"{settings.BASE_URL}/dashboard",
        cancel_url=f"{settings.BASE_URL}/product/{p.slug}"
    )
    return {"sessionId": session.id}

@order_router.post("/webhook")
async def stripe_webhook(request: Request, db=Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(400, "Invalid Stripe signature")
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_email"]
        product_name = session["display_items"][0]["custom"]["name"] if "display_items" in session else None
        user = db.query(User).filter_by(email=email).first()
        product = db.query(Product).filter_by(title=product_name).first()
        if user and product:
            order = Order(user_id=user.id, product_id=product.id, stripe_session_id=session["id"])
            db.add(order)
            db.commit()
            logger.info(f"Order created for {user.email}: {product.title}")
    return {"status": "success"}

# ----- AI PRODUCT GENERATION (LLM + PSYCH ENGINE) -----
class ProductPrompt(BaseModel):
    prompt: str

@api_router.post("/generate_product", response_model=dict)
def generate_product_api(body: ProductPrompt, user=Depends(get_current_user)):
    # LLM Gateway
    llm_resp = requests.post(
        settings.LLM_GATEWAY_URL,
        json={"prompt": body.prompt, "provider": "ollama", "model": "llama3", "max_tokens": 512},
        timeout=60
    )
    llm_text = llm_resp.json().get("response", "")
    # Pass through psych engine
    psych_resp = requests.post(
        f"{settings.PSYCH_ENGINE_URL}/personalize",
        json={"data": {"content": llm_text, "user_email": user.email}},
        timeout=15
    )
    out = psych_resp.json().get("content", llm_text)
    return {"product_copy": out}

# ----- HEALTH & DOCS -----
@app.get("/health")
def health():
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("claerk.html", {"request": request, "stripe_pub": settings.STRIPE_PUBLISHABLE_KEY})

# ----- MOUNT ROUTERS -----
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(api_router, prefix="/api", tags=["api"])

# ----- ERROR HANDLER -----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )
