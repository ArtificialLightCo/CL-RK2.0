# bots/base_bot.py — CLÆRK Universal BaseBot

import logging
import os

logger = logging.getLogger("claerk.basebot")

class BaseBot:
    """
    Universal bot interface for CLÆRK.
    Subclass this to make your own bot.
    """

    # Required metadata for all bots
    name = "BaseBot"
    description = "Universal bot base class"
    supported_platforms = []

    REQUIRED_ENV = []
    REQUIRED_LIBS = []

    def __init__(self, config=None):
        self.config = config or {}
        self.active = False

    def check_dependencies(self):
        """Check required Python packages and env vars."""
        issues = []
        for lib in self.REQUIRED_LIBS:
            try:
                __import__(lib)
            except ImportError:
                issues.append(f"Missing Python package: {lib}")
        for var in self.REQUIRED_ENV:
            if not os.environ.get(var):
                issues.append(f"Missing ENV: {var}")
        if issues:
            logger.warning(f"[{self.name}] Dependency issues: {issues}")
        else:
            logger.info(f"[{self.name}] All dependencies OK")
        return issues

    def setup(self):
        """Override in subclass for custom startup."""
        self.active = True
        logger.info(f"[{self.name}] Setup complete.")

    def run(self, *args, **kwargs):
        """Override in subclass. Main bot logic goes here."""
        logger.info(f"[{self.name}] Run called (override me).")

    def healthcheck(self):
        """Returns basic health info."""
        return {"ok": self.active, "name": self.name}

    def stop(self):
        self.active = False
        logger.info(f"[{self.name}] Stopped.")

# CLI for quick testing
if __name__ == "__main__":
    bot = BaseBot()
    bot.check_dependencies()
    bot.setup()
    bot.run()
    print(bot.healthcheck())
    bot.stop()
