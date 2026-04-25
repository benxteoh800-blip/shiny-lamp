"""
config.py – Central configuration loaded from environment variables.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Telegram ──────────────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ── OpenAI ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ── Bot behaviour ─────────────────────────────────────────────────────────
    # How many articles to fetch per news source
    ARTICLES_PER_SOURCE: int = int(os.getenv("ARTICLES_PER_SOURCE", "5"))
    # Cron-style schedule time (24-h, Malaysia Time UTC+8, e.g. "08:00")
    SCHEDULE_TIME: str = os.getenv("SCHEDULE_TIME", "08:00")
    # Whether to run immediately on startup (1 = yes, 0 = no)
    RUN_ON_START: bool = os.getenv("RUN_ON_START", "1") == "1"

    @classmethod
    def validate(cls) -> None:
        """Raise ValueError if required configuration is missing."""
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please copy .env.example to .env and fill in the values."
            )
