# product_generator.py — CLÆRK Advanced Product Generator

import os
import json
import random
from datetime import datetime
from pathlib import Path
import logging
import core  # Advanced persuasion engine
import sqlite3

try:
    from fastapi import FastAPI, Request
    from pydantic import BaseModel
except ImportError:
    FastAPI = None  # For CLI-only use

# -- Logging --
logger = logging.getLogger("claerk.product_gen")
logging.basicConfig(level=logging.INFO)

# -- DB setup (SQLite default) --
DB_PATH = os.environ.get("PRODUCT_DB", "claerk_products.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_to_db(product):
    conn = get_db()
    fields = ["title", "slug", "description", "price", "tags", "category", "created_at", "image", "persona", "product_type", "a_b_group", "locale"]
    placeholders = ",".join("?" for _ in fields)
    sql = f"INSERT INTO products ({','.join(fields)}) VALUES ({placeholders})"
    vals = [product.get(f) for f in fields]
    conn.execute(sql, vals)
    conn.commit()
    conn.close()
    logger.info(f"Saved product {product['slug']} to DB.")

def ensure_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, slug TEXT, description TEXT, price REAL, tags TEXT, category TEXT,
            created_at TEXT, image TEXT, persona TEXT, product_type TEXT,
            a_b_group TEXT, locale TEXT
        )
    """)
    conn.commit()
    conn.close()

ensure_db()

# -- Blueprint logic --
BLUEPRINTS = {
    "Productivity": {
        "pain_points": [
            "struggling to stay organized",
            "overwhelmed by tasks",
            "procrastination"
        ],
        "solutions": [
            "step-by-step action plans",
            "proven habit systems",
            "AI-powered daily routines"
        ]
    },
    "Mindset": {
        "pain_points": [
            "low motivation",
            "negative self-talk",
            "self-doubt"
        ],
        "solutions": [
            "confidence-boosting prompts",
            "psych-backed affirmations",
            "daily micro-challenges"
        ]
    }
    # Add blueprints for every niche you want!
}

CATEGORIES = list(BLUEPRINTS.keys())
PRODUCT_TYPES = ["guide", "checklist", "planner", "course", "bundle"]

# -- AI Image Generation --
def ai_generate_image(title, description, out_dir="product_images"):
    try:
        import requests
        # Example: local Stable Diffusion API
        sd_url = os.environ.get("SD_URL", "http://localhost:5000")
        resp = requests.post(
            f"{sd_url}/generate",
            json={"prompt": f"Cover for {title}: {description}", "steps": 30}
        )
        if resp.status_code == 200:
            Path(out_dir).mkdir(exist_ok=True)
            img_data = resp.content
            fname = Path(out_dir) / f"{title.lower().replace(' ', '_')}_{random.randint(1000,9999)}.png"
            with open(fname, "wb") as f:
                f.write(img_data)
            logger.info(f"AI image generated: {fname}")
            return str(fname)
    except Exception as e:
        logger.warning(f"AI image generation failed: {e}")
    # Fallback to Unsplash
    return f"https://source.unsplash.com/400x200/?{title.split()[0]}"

# -- Pricing psychology --
def smart_price(base=19.99, currency="$"):
    price = round(base * random.uniform(0.85, 1.15), 2)
    # Use psychological .99 pricing
    price = float(f"{int(price)}.99")
    return price

# -- Localization/translation (simple) --
def translate(text, locale="en"):
    # Add your translation logic here, or plug in DeepL/Google API
    return text  # Default: return as is

# -- Offer stack & content enrichment --
def build_offers(category, niche, persona, event=None):
    # Tiers: basic, pro, masterclass
    tiers = []
    for t in ["Basic", "Pro", "Masterclass"]:
        tiers.append({
            "title": f"{niche} {t}",
            "description": core.apply_principles(
                f"{t} tier: tailored {niche.lower()} solution for {persona or 'anyone'}.", 
                {"persona": persona, "niche": niche}
            ),
            "price": smart_price(19.99 + 20 * ["Basic","Pro","Masterclass"].index(t))
        })
    # Cross-sell: recommend other products
    cross_sell = f"Pair with our {random.choice(PRODUCT_TYPES).title()} for maximum results."
    # Content enrichment
    challenges = f"Try the 5-day {niche} challenge!"
    worksheet = f"Download the {niche} worksheet for step-by-step progress."
    # Event/season logic
    event_blurb = ""
    if event:
        event_blurb = f"Special for {event}: unlock exclusive bonuses!"
    return tiers, cross_sell, challenges, worksheet, event_blurb

# -- Main product generator --
def generate_product(
    persona="beginner",
    category=None,
    niche=None,
    product_type=None,
    locale="en",
    a_b_group=None,
    event=None,
    use_llm=False,
    context=None
):
    ensure_db()
    # Pick blueprint
    category = category or random.choice(CATEGORIES)
    blueprint = BLUEPRINTS.get(category, {})
    niche = niche or random.choice([n for n in blueprint.get("pain_points", [])])
    product_type = product_type or random.choice(PRODUCT_TYPES)
    pain = random.choice(blueprint.get("pain_points", ["general challenge"]))
    solution = random.choice(blueprint.get("solutions", ["proven system"]))
    context = context or {}
    context.update({"persona": persona, "category": category, "niche": niche, "pain_point": pain, "solution": solution, "product_type": product_type, "locale": locale})

    # Title, slug, price
    title = f"{niche.title()} {product_type.title()}"
    slug = title.lower().replace(" ", "-") + f"-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    price = smart_price()

    # Description: LLM or local
    if use_llm:
        try:
            import requests
            llm_resp = requests.post(
                os.environ.get("LLM_GATEWAY_URL", "http://localhost:9999/llm/generate"),
                json={"prompt": f"Write a persuasive {product_type} for {niche} ({pain}/{solution}), under 120 words, {locale}.", "provider": "ollama", "model": "llama3"},
                timeout=30
            )
            desc = llm_resp.json().get("response", "")
        except Exception as e:
            logger.warning(f"LLM fallback: {e}")
            desc = f"Your {product_type} to solve {pain} with {solution}."
    else:
        desc = f"Your {product_type} to solve {pain} with {solution}."

    # Persuasion
    full_desc = core.apply_principles(desc, context)
    # Image
    image = ai_generate_image(title, desc)
    # Offers/enrichment
    tiers, cross_sell, challenges, worksheet, event_blurb = build_offers(category, niche, persona, event)
    # Locale
    full_desc = translate(full_desc, locale)
    # A/B logic
    a_b_group = a_b_group or random.choice(["A", "B"])
    # Compile
    product = {
        "title": title, "slug": slug, "description": full_desc, "price": price,
        "tags": f"{category},{niche},{product_type}",
        "category": category, "created_at": datetime.utcnow().isoformat(),
        "image": image, "persona": persona, "product_type": product_type,
        "offers": tiers, "cross_sell": cross_sell, "challenge": challenges,
        "worksheet": worksheet, "event_blurb": event_blurb,
        "a_b_group": a_b_group, "locale": locale
    }
    save_to_db(product)
    save_product_json(product)
    return product

def save_product_json(product, output_dir="products"):
    Path(output_dir).mkdir(exist_ok=True)
    fpath = Path(output_dir) / f"product_{product['slug']}.json"
    with open(fpath, "w") as f:
        json.dump(product, f, indent=2)
    logger.info(f"Saved product: {fpath}")
    return fpath

# -- API Microservice (if FastAPI installed) --
if FastAPI:
    app = FastAPI(title="CLÆRK Product Generator")

    class ProductGenRequest(BaseModel):
        persona: str = "beginner"
        category: str = None
        niche: str = None
        product_type: str = None
        locale: str = "en"
        a_b_group: str = None
        event: str = None
        use_llm: bool = False

    @app.post("/generate", response_model=dict)
    async def generate_api(req: ProductGenRequest):
        p = generate_product(
            persona=req.persona, category=req.category, niche=req.niche,
            product_type=req.product_type, locale=req.locale, a_b_group=req.a_b_group,
            event=req.event, use_llm=req.use_llm
        )
        return p

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.get("/list", response_model=list)
    async def list_products(limit: int = 10):
        conn = get_db()
        rows = conn.execute("SELECT * FROM products ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    @app.post("/batch", response_model=list)
    async def batch_generate(batch: list[ProductGenRequest]):
        out = []
        for req in batch:
            p = generate_product(
                persona=req.persona, category=req.category, niche=req.niche,
                product_type=req.product_type, locale=req.locale, a_b_group=req.a_b_group,
                event=req.event, use_llm=req.use_llm
            )
            out.append(p)
        return out

# -- CLI Usage --
if __name__ == "__main__":
    product = generate_product(persona="beginner", use_llm=False)
    print(json.dumps(product, indent=2))
