# core.py — CLÆRK 2.0 Persuasion Engine (All Cognitive Biases + Ultra Advanced)
import random
import logging
from datetime import datetime
import importlib
import os

logger = logging.getLogger("claerk.psych")
logging.basicConfig(level=logging.INFO)

# --- Core: Cognitive Biases & Principles (with multiple copy variants) ---

PERSUASION_LIBRARY = {
    "loss_aversion": [
        "Don’t risk missing out—waiting may cost you more than you think.",
        "Lost time can’t be regained—take action now!",
        "What you stand to lose by waiting is greater than what you might gain later."
    ],
    "social_proof": [
        "Join our thriving community of successful users.",
        "See why thousands trust this system.",
        "Backed by real user results."
    ],
    "scarcity": [
        "Only a limited number available—act now!",
        "This exclusive offer is ending soon!",
        "Last spots remaining—don’t miss your chance."
    ],
    "fomo": [
        "Others are signing up now—don’t get left behind!",
        "Don’t miss out—secure your spot while you can.",
        "Your friends may already be inside!"
    ],
    "anchoring": [
        "Regularly {anchor}, but today only {price}.",
        "Compare at {anchor}, yours now for just {price}!",
        "Was {anchor}—now save big at {price}."
    ],
    # ... All other principles with 2–3 copy variants each ...
}

PRINCIPLES = list(PERSUASION_LIBRARY.keys())

# --- Persona, Multilingual, and Cultural Libraries ---
PERSONA_LIBRARY = {
    "beginner": "Start strong with guidance made for newcomers.",
    "pro": "Advanced strategies for seasoned experts.",
    "parent": "Family-friendly, easy-to-implement solutions.",
    "student": "Perfect for busy learners."
}

CULTURE_LIBRARY = {
    "en": {
        "social_proof": [
            "Most popular in the US and UK.",
            "Americans love this plan!"
        ],
        "authority": [
            "Endorsed by U.S. experts."
        ]
    },
    "jp": {
        "authority": [
            "Recommended by leading Japanese professionals."
        ],
        "social_proof": [
            "Chosen by thousands in Japan."
        ]
    }
    # Add more as you localize!
}

# --- Conversion Analytics Adapter (for adaptive principle weighting) ---
# You can wire this to Stripe, analytics events, or even a DB
class ConversionAnalytics:
    def __init__(self):
        self.weights = {k: 1.0 for k in PRINCIPLES}

    def update_weights(self, principle, success=True):
        if success:
            self.weights[principle] += 0.1
        else:
            self.weights[principle] = max(0.1, self.weights[principle] - 0.1)

    def get_weighted_order(self):
        ordered = sorted(self.weights, key=lambda k: -self.weights[k])
        logger.info(f"Principle order by weights: {ordered}")
        return ordered

analytics = ConversionAnalytics()

# --- Plugin Loader ---
def load_plugins(plugin_folder="principles"):
    """Auto-load all plugin modules in /principles/ directory."""
    loaded = []
    if not os.path.isdir(plugin_folder):
        return loaded
    for fname in os.listdir(plugin_folder):
        if fname.endswith(".py") and not fname.startswith("_"):
            modname = f"{plugin_folder}.{fname[:-3]}"
            try:
                loaded.append(importlib.import_module(modname))
            except Exception as e:
                logger.error(f"Plugin load error {modname}: {e}")
    return loaded

PLUGINS = load_plugins()

# --- Helper Functions ---
def pick_variant(principle, ctx):
    variants = PERSUASION_LIBRARY.get(principle, [])
    if not variants:
        return ""
    # Cultural adaptation
    lang = ctx.get("lang") if ctx else "en"
    culture_overrides = CULTURE_LIBRARY.get(lang, {}).get(principle)
    if culture_overrides:
        variants += culture_overrides
    template = random.choice(variants)
    # Anchor/price for anchoring, others can be extended
    if "{anchor}" in template:
        template = template.replace("{anchor}", ctx.get("anchor_price", "$99"))
    if "{price}" in template:
        template = template.replace("{price}", ctx.get("offer_price", "$19"))
    return template

def persona_line(ctx):
    persona = ctx.get("persona")
    return PERSONA_LIBRARY.get(persona, "") if persona else ""

def progress_illusion(ctx):
    progress = ctx.get("progress_pct") if ctx and ctx.get("progress_pct") else random.randint(70,95)
    return f"You’re {progress}% finished—complete your journey now!"

def device_context(ctx):
    device = ctx.get("device")
    if device == "mobile":
        return "On-the-go? This is mobile-optimized."
    elif device == "desktop":
        return "Settle in—perfect for deep work sessions."
    return ""

def time_context(ctx):
    hour = ctx.get("hour", datetime.utcnow().hour)
    if 22 <= hour or hour < 6:
        return "Night owl bonus: Get a fresh start tomorrow!"
    elif 8 <= hour <= 11:
        return "Morning focus—start your day right."
    return ""

def first_time_encouragement(ctx):
    if ctx.get("first_time_buyer"):
        return "You’re starting strong—many have begun with this step and seen real results."
    return ""

def user_feedback_line(ctx):
    if ctx.get("real_stats"):
        return ctx["real_stats"]
    return ""

def emotion_line(ctx):
    mood = ctx.get("emotion")
    if mood == "anxious":
        return "Feeling uncertain? This is designed to bring clarity."
    elif mood == "motivated":
        return "Ride your motivation—unlock results faster!"
    elif mood == "frustrated":
        return "You’re not alone—this guide is built to solve that exact challenge."
    return ""

def live_social_proof(ctx):
    live = ctx.get("live_blurb")
    return live if live else ""

# --- Adaptive Bias/Principle Engine ---

def apply_principles(
    text, ctx=None,
    num_biases=8,
    randomize=False,
    multilingual=True,
    plugins=True,
    analytics_update=None,
    log=True
):
    """
    Applies cognitive biases, context, and persona logic to the base text.
    :param text: The original copy.
    :param ctx: Context dict (persona, lang, device, first_time_buyer, etc.).
    :param num_biases: How many principles to apply per output (rotate/test/A/B).
    :param randomize: Use random ordering (otherwise weighted/adaptive).
    :param multilingual: Enable culture/language adaptation.
    :param plugins: Load external plugins from /principles/.
    :param analytics_update: callback for conversion tracking.
    :param log: log the process
    :return: Persuasion-optimized text
    """
    ctx = ctx or {}
    lang = ctx.get("lang", "en")
    output_lines = [text]

    # 1. Persona and context
    pline = persona_line(ctx)
    if pline:
        output_lines.append(pline)
    if first_time_encouragement(ctx):
        output_lines.append(first_time_encouragement(ctx))
    if device_context(ctx):
        output_lines.append(device_context(ctx))
    if time_context(ctx):
        output_lines.append(time_context(ctx))
    if progress_illusion(ctx):
        output_lines.append(progress_illusion(ctx))
    if user_feedback_line(ctx):
        output_lines.append(user_feedback_line(ctx))
    if emotion_line(ctx):
        output_lines.append(emotion_line(ctx))
    if live_social_proof(ctx):
        output_lines.append(live_social_proof(ctx))

    # 2. Bias/principle ordering
    if randomize:
        selected = random.sample(PRINCIPLES, min(num_biases, len(PRINCIPLES)))
    else:
        # Weighted/adaptive ordering (from analytics feedback)
        selected = analytics.get_weighted_order()[:num_biases]

    for pr in selected:
        line = pick_variant(pr, ctx)
        if line:
            output_lines.append(line)
        if analytics_update:
            analytics_update(pr, success=None)  # Optionally call after real conversion

    # 3. Plugin system (optional, e.g., /principles/ directory)
    if plugins and PLUGINS:
        for plugin in PLUGINS:
            try:
                output_lines.append(plugin.inject(ctx=ctx))
            except Exception as e:
                logger.error(f"Plugin error: {e}")

    # 4. Multilingual/cultural re-inject (for end cap)
    if multilingual and lang in CULTURE_LIBRARY:
        for pr, lines in CULTURE_LIBRARY[lang].items():
            output_lines += lines

    result = " ".join([str(line) for line in output_lines if line])
    if log:
        logger.info(f"Applied principles: {selected} + persona/context for {ctx.get('persona', 'unknown')}")
    return result

# --- Example Usage ---
if __name__ == "__main__":
    base = "Unlock your productivity with this new digital planner."
    context = {
        "persona": "beginner",
        "lang": "en",
        "anchor_price": "$89",
        "offer_price": "$19",
        "main_benefit": "Immediate Results",
        "device": "mobile",
        "hour": 22,
        "progress_pct": 83,
        "first_time_buyer": True,
        "real_stats": "Over 2,500 real customers worldwide.",
        "emotion": "motivated",
        "live_blurb": "Anna from Berlin just purchased.",
    }
    print(apply_principles(base, context, randomize=False))
