# plugins/plugin_loader.py — CLÆRK Plugin Auto-loader

import logging
import os
import importlib
from pathlib import Path

logger = logging.getLogger("claerk.plugin_loader")
PLUGIN_DIR = Path(__file__).parent

class BasePlugin:
    """
    Universal plugin interface for CLÆRK.
    Subclass this and implement `inject(ctx)` or `run(ctx)`.
    """
    name = "BasePlugin"
    description = "Universal plugin base class"

    def inject(self, ctx):
        raise NotImplementedError

def load_plugins(plugin_dir=PLUGIN_DIR):
    """Auto-load all plugin modules in the plugins directory."""
    plugins = []
    for py in plugin_dir.glob("*.py"):
        if py.name.startswith("__") or py.stem == "plugin_loader":
            continue
        try:
            mod = importlib.import_module(f"plugins.{py.stem}")
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugins.append(attr())
                    logger.info(f"Loaded plugin: {attr.name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {py.stem}: {e}")
    return plugins

# Example usage
if __name__ == "__main__":
    plugins = load_plugins()
    print([p.name for p in plugins])
