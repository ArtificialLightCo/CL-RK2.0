# bots/BOT_REGISTRY.py — CLÆRK Universal Bot Orchestrator

import os
import sys
import logging
import importlib
from pathlib import Path
from types import ModuleType

logger = logging.getLogger("claerk.bot_registry")
logging.basicConfig(level=logging.INFO)

BOTS_DIR = Path(__file__).parent
BOT_CONFIG = {
    # "genesis_prime": {"enabled": True},
    # "affiliate_marketing_bot": {"enabled": True},
    # Add bot_name: {config...} to override defaults
}

def find_bot_modules():
    bots = []
    for py in BOTS_DIR.glob("*.py"):
        if py.name.startswith("__") or py.name == "BOT_REGISTRY.py":
            continue
        bot_name = py.stem
        try:
            mod = importlib.import_module(f"bots.{bot_name}")
            bots.append((bot_name, mod))
        except Exception as e:
            logger.error(f"Error importing {bot_name}: {e}")
    return bots

def get_bot_class(module: ModuleType):
    # Looks for a class with "Bot" in name or a "run" function
    for name in dir(module):
        attr = getattr(module, name)
        if isinstance(attr, type) and "Bot" in name:
            return attr
    if hasattr(module, "run"):
        return module.run
    return None

def list_bots():
    discovered = find_bot_modules()
    bots = []
    for bot_name, mod in discovered:
        cls = get_bot_class(mod)
        if cls:
            enabled = BOT_CONFIG.get(bot_name, {}).get("enabled", True)
            desc = getattr(cls, "description", None) or getattr(mod, "__doc__", "")
            bots.append({"name": bot_name, "enabled": enabled, "class": cls, "description": desc})
    return bots

def run_bot(bot_name, *args, **kwargs):
    for bot in list_bots():
        if bot["name"] == bot_name and bot["enabled"]:
            cls = bot["class"]
            logger.info(f"Starting bot: {bot_name}")
            try:
                if isinstance(cls, type):
                    instance = cls()
                    if hasattr(instance, "run"):
                        instance.run(*args, **kwargs)
                elif callable(cls):
                    cls(*args, **kwargs)
                logger.info(f"Bot {bot_name} completed.")
            except Exception as e:
                logger.error(f"Bot {bot_name} failed: {e}")
            return
    logger.warning(f"Bot {bot_name} not found or not enabled.")

def run_all_bots():
    for bot in list_bots():
        if bot["enabled"]:
            run_bot(bot["name"])

def check_bot_dependencies():
    issues = []
    for bot in list_bots():
        try:
            mod = importlib.import_module(f"bots.{bot['name']}")
            if hasattr(mod, "REQUIRED_LIBS"):
                for lib in mod.REQUIRED_LIBS:
                    try:
                        importlib.import_module(lib)
                    except ImportError:
                        issues.append(f"Bot '{bot['name']}' missing dependency: {lib}")
        except Exception as e:
            issues.append(f"Bot '{bot['name']}' import error: {e}")
    if issues:
        logger.warning("\n".join(issues))
    else:
        logger.info("All bot dependencies satisfied.")
    return issues

# Optional: API server for bot control
try:
    from fastapi import FastAPI
    app = FastAPI(title="CLÆRK Bot Control API")

    @app.get("/bots")
    def api_list():
        return [{"name": b["name"], "enabled": b["enabled"], "description": b["description"]} for b in list_bots()]

    @app.post("/run/{bot_name}")
    def api_run(bot_name: str):
        run_bot(bot_name)
        return {"ok": True}

    @app.post("/run_all")
    def api_run_all():
        run_all_bots()
        return {"ok": True}

    @app.get("/health")
    def api_health():
        return {"ok": True, "bots": [b["name"] for b in list_bots()]}

except ImportError:
    pass  # FastAPI not installed

# CLI Usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CLÆRK Bot Registry")
    parser.add_argument("--list", action="store_true", help="List bots")
    parser.add_argument("--run", type=str, help="Run a bot by name")
    parser.add_argument("--run_all", action="store_true", help="Run all enabled bots")
    parser.add_argument("--check", action="store_true", help="Check bot dependencies")
    args = parser.parse_args()

    if args.list:
        for b in list_bots():
            print(f"{b['name']}: {'ENABLED' if b['enabled'] else 'DISABLED'} — {b['description']}")
    elif args.run:
        run_bot(args.run)
    elif args.run_all:
        run_all_bots()
    elif args.check:
        check_bot_dependencies()
    else:
        parser.print_help()
