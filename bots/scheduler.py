# scheduler.py — CLÆRK Celery Scheduler/Worker

import os
import logging
from celery import Celery
from datetime import datetime
import random

# --- Celery config ---
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("claerk", broker=REDIS_URL, backend=REDIS_URL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claerk.scheduler")

# --- Example: import bots and generator ---
from bots import BOT_REGISTRY
from product_generator import generate_product

# --- Scheduled: Traffic/Campaign Bots ---
@celery.task
def run_bot(bot_name):
    logger.info(f"[Celery] Running bot: {bot_name}")
    BOT_REGISTRY.run_bot(bot_name)

@celery.task
def run_all_bots():
    logger.info("[Celery] Running all enabled bots")
    BOT_REGISTRY.run_all_bots()

# --- Scheduled: Batch Product Generation ---
@celery.task
def batch_generate_products(num=10, persona="beginner"):
    logger.info(f"[Celery] Generating {num} products")
    for _ in range(num):
        generate_product(persona=persona)
    logger.info(f"[Celery] Batch generation done")

# --- Scheduled: Report/Email/Alert (stub) ---
@celery.task
def send_admin_alert(subject, message):
    logger.info(f"[Celery] Admin Alert: {subject} — {message}")
    # Integrate email/Slack/Telegram as needed

# --- Healthcheck ---
@celery.task
def healthcheck():
    logger.info(f"[Celery] Healthcheck @ {datetime.utcnow()}")
    return {"ok": True, "time": datetime.utcnow().isoformat()}

# --- CLI ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CLÆRK Scheduler CLI")
    parser.add_argument("--run_bot", type=str, help="Run a single bot by name")
    parser.add_argument("--run_all", action="store_true", help="Run all enabled bots")
    parser.add_argument("--batch_gen", type=int, help="Batch generate N products")
    parser.add_argument("--health", action="store_true", help="Run healthcheck")
    args = parser.parse_args()

    if args.run_bot:
        run_bot.delay(args.run_bot)
    elif args.run_all:
        run_all_bots.delay()
    elif args.batch_gen:
        batch_generate_products.delay(args.batch_gen)
    elif args.health:
        healthcheck.delay()
    else:
        parser.print_help()

# --- API endpoints (optional, if FastAPI is installed) ---
try:
    from fastapi import FastAPI
    app = FastAPI(title="CLÆRK Scheduler API")

    @app.post("/run_bot/{bot_name}")
    async def api_run_bot(bot_name: str):
        run_bot.delay(bot_name)
        return {"ok": True}

    @app.post("/run_all")
    async def api_run_all():
        run_all_bots.delay()
        return {"ok": True}

    @app.post("/batch_generate")
    async def api_batch_generate(num: int = 10, persona: str = "beginner"):
        batch_generate_products.delay(num, persona)
        return {"ok": True}

    @app.get("/health")
    async def api_health():
        healthcheck.delay()
        return {"ok": True}

except ImportError:
    pass  # FastAPI not installed
