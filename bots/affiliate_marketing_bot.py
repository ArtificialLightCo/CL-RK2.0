# bots/affiliate_marketing_bot.py — CLÆRK Universal Affiliate Bot (Global Edition)

import os
import logging
import random
import csv
import core  # Persuasion engine
import requests
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("claerk.affiliatebot")
logging.basicConfig(level=logging.INFO)

# -- Load offer URLs and proxies --
AFFILIATE_LINKS = os.environ.get("AFFILIATE_LINKS", "https://your-link.com").split(",")
PROXY_LIST = os.environ.get("BOT_PROXIES", "").split(",") if os.environ.get("BOT_PROXIES") else []

# -- Hot offers (auto-pulled or static for now) --
HOT_OFFERS = [
    "https://best-affiliate-network.com/hot-offer-1",
    "https://another-affiliate.com/trending"
    # TODO: Wire to ClickBank, Amazon, etc. API for live trending
]

# -- Platform Class Stubs (modular, fill as you get API keys) --
class BasePlatformPoster:
    """Base class for all platform posters"""
    def __init__(self, config):
        self.config = config
    def post(self, *args, **kwargs):
        logger.info(f"[{self.__class__.__name__}] Would post: {args} {kwargs}")

# Example for the first few...
class BlogspotPoster(BasePlatformPoster): pass
class BlueSkyPoster(BasePlatformPoster): pass
class ClubhousePoster(BasePlatformPoster): pass
class DiasporaPoster(BasePlatformPoster): pass
class DiscordPoster(BasePlatformPoster): pass
class DoubanPoster(BasePlatformPoster): pass
class FacebookPoster(BasePlatformPoster): pass
class GabPoster(BasePlatformPoster): pass
class HivePoster(BasePlatformPoster): pass
class InstagramPoster(BasePlatformPoster): pass
class KakaoPoster(BasePlatformPoster): pass
class LinePoster(BasePlatformPoster): pass
class LinkedInPoster(BasePlatformPoster): pass
class MastodonPoster(BasePlatformPoster): pass
class MediumPoster(BasePlatformPoster): pass
class MixPoster(BasePlatformPoster): pass
class NostrPoster(BasePlatformPoster): pass
class OdyseePoster(BasePlatformPoster): pass
class PeertubePoster(BasePlatformPoster): pass
class PinterestPoster(BasePlatformPoster): pass
class QuoraPoster(BasePlatformPoster): pass
class RedditPoster(BasePlatformPoster): pass
class RumblePoster(BasePlatformPoster): pass
class SignalPoster(BasePlatformPoster): pass
class SinaWeiboPoster(BasePlatformPoster): pass
class SlackPoster(BasePlatformPoster): pass
class SnapchatPoster(BasePlatformPoster): pass
class SubstackPoster(BasePlatformPoster): pass
class TelegramPoster(BasePlatformPoster): pass
class ThreadsPoster(BasePlatformPoster): pass
class TikTokPoster(BasePlatformPoster): pass
class TumblrPoster(BasePlatformPoster): pass
class TwitchPoster(BasePlatformPoster): pass
class TwitterPoster(BasePlatformPoster): pass
class ViberPoster(BasePlatformPoster): pass
class VKPoster(BasePlatformPoster): pass
class WeiboPoster(BasePlatformPoster): pass
class WechatPoster(BasePlatformPoster): pass
class WhatsAppPoster(BasePlatformPoster): pass
class WordPressPoster(BasePlatformPoster): pass
class YouTubePoster(BasePlatformPoster): pass

# --- Additional regional/niche/global platforms ---
class BaiduTiebaPoster(BasePlatformPoster): pass
class QZonePoster(BasePlatformPoster): pass
class ZhihuPoster(BasePlatformPoster): pass
class XINGPoster(BasePlatformPoster): pass
class BadooPoster(BasePlatformPoster): pass
class MeetupPoster(BasePlatformPoster): pass
class FoursquarePoster(BasePlatformPoster): pass
class VKGroupsPoster(BasePlatformPoster): pass
class TaringaPoster(BasePlatformPoster): pass
class ViadeoPoster(BasePlatformPoster): pass
class SnapPoster(BasePlatformPoster): pass
class MySpacePoster(BasePlatformPoster): pass
class GoodreadsPoster(BasePlatformPoster): pass
class NextdoorPoster(BasePlatformPoster): pass
class YammerPoster(BasePlatformPoster): pass
class ProductHuntPoster(BasePlatformPoster): pass
class HackerNewsPoster(BasePlatformPoster): pass
class AngelListPoster(BasePlatformPoster): pass
class BehancePoster(BasePlatformPoster): pass
class DribbblePoster(BasePlatformPoster): pass
class DeviantArtPoster(BasePlatformPoster): pass
class SoundCloudPoster(BasePlatformPoster): pass
class LetterboxdPoster(BasePlatformPoster): pass
class StackOverflowPoster(BasePlatformPoster): pass
class ResearchGatePoster(BasePlatformPoster): pass
class PatreonPoster(BasePlatformPoster): pass
class KoFiPoster(BasePlatformPoster): pass
class PayhipPoster(BasePlatformPoster): pass

# -- ALL platform classes in one dictionary for easy enable/disable --
PLATFORM_CLASSES = {
    k.lower().replace("poster", ""): v for k, v in locals().items()
    if k.endswith("Poster") and k != "BasePlatformPoster"
}

# --- Compliance Checker ---
BANNED_WORDS = ["guaranteed", "get rich quick", "easy money", "instant profit"]
def is_compliant(text):
    for word in BANNED_WORDS:
        if word.lower() in text.lower():
            logger.warning(f"Compliance warning: Banned word '{word}' found.")
            return False
    return True

# --- Hot Offer Rotation ---
def pick_hot_offer():
    # In production, this could hit affiliate network APIs for live trending offers.
    return random.choice(HOT_OFFERS + AFFILIATE_LINKS)

# --- Deep-link personalization ---
def personalize_link(link, user_id=None, session_id=None):
    if user_id:
        link += f"?ref_user={user_id}"
    if session_id:
        link += f"&sid={session_id}"
    return link

# --- Webhook/Callback stub ---
def on_conversion(event):
    logger.info(f"Conversion event: {event}")
    # Here, you could trigger a webhook, email, Slack, dashboard update, etc.

# --- Cross-promotion stacking ---
def cross_promote(product, main_link, persona=None):
    # Schedules a followup offer after primary
    msg = f"Love {product['title']}? Check out our related offer for {persona or 'you'}!"
    logger.info(f"[Cross-promotion] {msg}")
    # You can queue this for later, or send to DMs, etc.

# --- Language/translation ---
def translate(text, lang="en"):
    # Integrate Google Translate, DeepL, or OSS later
    return text

# --- Stealth/undetectable anti-ban ---
def stealthify_message(msg):
    # Mimic human patterns, randomize emoji, etc.
    typo_chance = 0.1
    if random.random() < typo_chance:
        pos = random.randint(0, len(msg)-2)
        msg = msg[:pos] + msg[pos+1] + msg[pos] + msg[pos+2:]
    if random.random() < 0.2:
        msg += " " + random.choice(["😊", "🔥", "🚀", "👍"])
    return msg

# --- Persona/context-aware copy ---
def generate_affiliate_message(product, link, persona="beginner", platform=None, variant=None, use_llm=True, context=None, lang="en"):
    context = context or {}
    base = f"Check out {product['title']} — {product['description']} ({link})"
    context.update({
        "persona": persona,
        "platform": platform,
        "main_benefit": product.get("category"),
        "product_type": product.get("product_type"),
        "locale": lang,
        "a_b_group": variant,
    })
    msg = base
    if use_llm:
        try:
            resp = requests.post(
                os.environ.get("LLM_GATEWAY_URL", "http://localhost:9999/llm/generate"),
                json={
                    "prompt": f"Write a high-conversion, compliant affiliate post for {platform or 'social'} about {product['title']}: {product['description']} with link: {link}. Persona: {persona}. Variant: {variant or 'A'}. Language: {lang}.",
                    "provider": "ollama", "model": "llama3", "max_tokens": 180
                },
                timeout=20
            )
            msg = resp.json().get("response", base)
        except Exception as e:
            logger.warning(f"LLM error for {platform}: {e}")
    persuasive = core.apply_principles(msg, context)
    translated = translate(persuasive, lang)
    final_msg = stealthify_message(translated)
    logger.info(f"Generated affiliate promo for {platform}: {final_msg}")
    return final_msg

# --- Analytics/Performance Tracking ---
def log_performance(data, out_file="affiliate_performance.csv"):
    file_exists = Path(out_file).exists()
    with open(out_file, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    logger.info(f"Logged affiliate performance: {data}")

# --- Modular posting ---
def post_affiliate_message(product, link, platform, persona="beginner", variant=None, use_llm=True, campaign="main", lang="en", user_id=None, session_id=None):
    personalized_link = personalize_link(link, user_id, session_id)
    message = generate_affiliate_message(product, personalized_link, persona=persona, platform=platform, variant=variant, use_llm=use_llm, lang=lang)
    if not is_compliant(message):
        logger.warning(f"Message NOT compliant for {platform}, skipping.")
        return
    poster_class = PLATFORM_CLASSES.get(platform)
    if not poster_class:
        logger.info(f"[DRY RUN] Would post to {platform}: {message}")
        return
    try:
        poster = poster_class({})  # Pass real config as needed
        poster.post(product['title'], message)
        logger.info(f"[{platform}] Affiliate post sent.")
        log_performance({
            "datetime": datetime.utcnow().isoformat(),
            "platform": platform,
            "persona": persona,
            "variant": variant or "A",
            "campaign": campaign,
            "product": product['title'],
            "link": personalized_link
        })
        cross_promote(product, personalized_link, persona)
    except Exception as e:
        logger.error(f"[{platform}] Affiliate post failed: {e}")

# --- Campaign Runner ---
def run_affiliate_campaign(
    products,
    platforms=None,
    persona="beginner",
    variants=["A", "B"],
    schedule_delay=0,
    campaign="main",
    use_llm=True,
    lang="en"
):
    platforms = platforms or list(PLATFORM_CLASSES.keys())
    links = [pick_hot_offer()]  # Rotates hot offer for each run
    for product in products:
        for link in links:
            for platform in platforms:
                for variant in variants:
                    post_affiliate_message(
                        product, link, platform, persona=persona, variant=variant,
                        use_llm=use_llm, campaign=campaign, lang=lang
                    )
                    time.sleep(schedule_delay)  # Anti-ban

# --- CLI/Batch/Proxy rotation ---
def rotate_proxy():
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

def load_products_from_json(product_dir="products"):
    files = Path(product_dir).glob("*.json")
    return [json.load(open(f)) for f in files]

def main_cli():
    import argparse
    parser = argparse.ArgumentParser(description="Affiliate Marketing Bot (Global)")
    parser.add_argument("--platforms", nargs="+", default=list(PLATFORM_CLASSES.keys()), help="Platforms")
    parser.add_argument("--product_dir", default="products", help="Product JSONs dir")
    parser.add_argument("--persona", default="beginner", help="Persona")
    parser.add_argument("--variants", nargs="+", default=["A", "B"], help="A/B variants")
    parser.add_argument("--schedule_delay", type=int, default=15, help="Seconds between posts")
    parser.add_argument("--dry_run", action="store_true", help="Do not actually post")
    parser.add_argument("--lang", default="en", help="Language code")
    args = parser.parse_args()

    products = load_products_from_json(args.product_dir)
    if args.dry_run:
        for product in products:
            for platform in args.platforms:
                print(f"[DRY RUN] Would post to {platform}: {product['title']}")
        return
    run_affiliate_campaign(
        products, platforms=args.platforms, persona=args.persona, variants=args.variants,
        schedule_delay=args.schedule_delay, lang=args.lang
    )

if __name__ == "__main__":
    main_cli()
