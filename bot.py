"""
bot.py – Main entry point for the Malaysia Motorcycle Launch Telegram Bot.

Usage:
    python bot.py            # run immediately and then on the configured schedule
    python bot.py --once     # run once and exit (useful for cron jobs)
    python bot.py --test     # send a test message to verify Telegram is working
"""

import argparse
import logging
import sys
import time

import schedule

from analyzer import analyze_motorcycle
from config import Config
from scraper import get_latest_motorcycle_launches
from telegram_sender import send_launch_update, send_status_message

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("moto_bot")


def run_bot() -> None:
    """
    Core pipeline:
      1. Scrape latest motorcycle launch articles from Malaysian news sites.
      2. For each article, query OpenAI for Malaysia-specific pros/cons.
      3. Send a formatted message to the configured Telegram chat.
    """
    logger.info("=== Motorcycle Malaysia Bot — starting run ===")

    articles = get_latest_motorcycle_launches(Config.ARTICLES_PER_SOURCE)

    if not articles:
        logger.warning("No articles found. The news sites may have changed their HTML structure.")
        send_status_message(
            "⚠️ <b>Malaysia Moto Bot</b>\nNo new motorcycle launch articles were found this time. "
            "Will try again at the next scheduled run."
        )
        return

    logger.info("Processing %d article(s)…", len(articles))

    for i, article in enumerate(articles, start=1):
        logger.info("[%d/%d] Analyzing: %s", i, len(articles), article.get("bike_name", article["title"]))

        analysis = analyze_motorcycle(article)
        success = send_launch_update(article, analysis)

        if success:
            logger.info("  ✓ Message sent to Telegram.")
        else:
            logger.error("  ✗ Failed to send message for: %s", article["title"])

        # Small delay to respect API rate limits
        if i < len(articles):
            time.sleep(2)

    logger.info("=== Run complete. %d update(s) sent. ===", len(articles))


def send_test_message() -> None:
    """Send a simple connectivity test to Telegram."""
    ok = send_status_message(
        "✅ <b>Malaysia Moto Bot – Test Message</b>\n\n"
        "If you can read this, your bot is configured correctly! 🏍️"
    )
    if ok:
        print("✓ Test message sent successfully.")
    else:
        print("✗ Failed to send test message. Check your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Malaysia Motorcycle Launch Telegram Bot")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--test", action="store_true", help="Send a test message and exit")
    args = parser.parse_args()

    # Validate config before doing anything
    try:
        Config.validate()
    except ValueError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    if args.test:
        send_test_message()
        return

    if args.once:
        run_bot()
        return

    # ── Continuous / scheduled mode ───────────────────────────────────────────
    if Config.RUN_ON_START:
        run_bot()

    logger.info("Scheduling daily runs at %s (server local time).", Config.SCHEDULE_TIME)
    schedule.every().day.at(Config.SCHEDULE_TIME).do(run_bot)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
