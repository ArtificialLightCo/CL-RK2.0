# psych_engine.py — CLÆRK Persuasion Engine API Wrapper

import logging
import core  # Import your advanced core.py persuasion engine

logger = logging.getLogger("claerk.psych_engine")

class PsychEngine:
    def __init__(self, model_version="v2"):
        self.model_version = model_version
        self.core = core  # Allows for engine swap if needed

    async def personalize(self, content, ctx):
        """Apply full persuasion/adaptive stack to content and context."""
        try:
            result = self.core.apply_principles(content, ctx)
            logger.info(f"[PsychEngine] Personalized content for {ctx.get('persona', 'user')}")
            return result
        except Exception as e:
            logger.error(f"Personalize error: {e}")
            return content

    async def inject(self, content, ctx):
        """Apply only primary persuasion principles (no advanced context)."""
        try:
            result = self.core.apply_principles(
                content, ctx, advanced=False, log=True
            )
            logger.info(f"[PsychEngine] Injected principles for {ctx.get('persona', 'user')}")
            return result
        except Exception as e:
            logger.error(f"Inject error: {e}")
            return content

    async def select_strategy(self, ctx):
        """Suggest a persuasion strategy or stack based on persona/context."""
        persona = ctx.get("persona", "default")
        if persona == "beginner":
            return ["liking", "commitment", "social_proof", "loss_aversion"]
        elif persona == "pro":
            return ["anchoring", "authority", "salience", "scarcity"]
        # Add more persona/segment strategies here
        return ["loss_aversion", "social_proof", "scarcity"]

    async def get_supported_principles(self):
        """List all principles/advanced functions supported by this engine."""
        base = core.PRINCIPLES
        advanced = [f.__name__ for f in core.ADVANCED_FUNCS]
        return {"principles": base, "advanced": advanced}

    async def health(self):
        return {"ok": True, "version": self.model_version}

# Example: (synchronous test)
if __name__ == "__main__":
    engine = PsychEngine()
    ctx = core.build_ctx(persona="beginner", first_time_buyer=True)
    text = "Unlock your potential with this digital planner."
    import asyncio
    print(asyncio.run(engine.personalize(text, ctx)))
