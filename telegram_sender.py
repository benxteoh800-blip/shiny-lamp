"""
telegram_sender.py – Sends formatted motorcycle update messages via Telegram Bot API.
"""

import logging
from typing import Optional

import requests

from config import Config

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"
MAX_MESSAGE_LENGTH = 4096  # Telegram hard limit


def _api_url(method: str) -> str:
    return TELEGRAM_API_BASE.format(token=Config.TELEGRAM_BOT_TOKEN, method=method)


def send_message(text: str, chat_id: Optional[str] = None, parse_mode: str = "HTML") -> bool:
    """
    Send a text message to the configured Telegram chat.

    Args:
        text:       Message content (HTML or MarkdownV2 formatted).
        chat_id:    Override the default chat_id from Config.
        parse_mode: "HTML" (default) or "MarkdownV2".

    Returns:
        True on success, False on failure.
    """
    target_chat = chat_id or Config.TELEGRAM_CHAT_ID
    if not target_chat:
        logger.error("No Telegram CHAT_ID configured.")
        return False

    # Telegram has a 4096-char limit; split if necessary
    chunks = _split_message(text, MAX_MESSAGE_LENGTH)
    success = True
    for chunk in chunks:
        payload = {
            "chat_id": target_chat,
            "text": chunk,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }
        try:
            response = requests.post(
                _api_url("sendMessage"),
                json=payload,
                timeout=15,
            )
            data = response.json()
            if not data.get("ok"):
                logger.error("Telegram API error: %s", data.get("description", "Unknown error"))
                success = False
        except requests.RequestException as exc:
            logger.error("Failed to send Telegram message: %s", exc)
            success = False

    return success


def _split_message(text: str, max_len: int) -> list[str]:
    """Split a long message into chunks that respect the Telegram character limit."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while len(text) > max_len:
        # Try to split at a newline boundary
        split_pos = text.rfind("\n", 0, max_len)
        if split_pos == -1:
            split_pos = max_len
        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks


def format_launch_message(article: dict, analysis: Optional[dict]) -> str:
    """
    Build a nicely formatted HTML message for a motorcycle launch.

    Args:
        article:  Scraper result dict (title, url, source, bike_name, fetched_at).
        analysis: Analyzer result dict (pros, cons, summary), or None.

    Returns:
        HTML-formatted string ready to send via Telegram.
    """
    title = _esc(article.get("title", "New Motorcycle Launch"))
    bike_name = _esc(article.get("bike_name", ""))
    url = article.get("url", "")
    source = _esc(article.get("source", ""))

    lines = [
        "🏍️ <b>Malaysia Motorcycle Launch Update</b>",
        "",
        f"📰 <b>{title}</b>",
    ]

    if url:
        lines.append(f'🔗 <a href="{url}">Read full article</a> — {source}')

    if analysis:
        summary = _esc(analysis.get("summary", ""))
        pros = analysis.get("pros", [])
        cons = analysis.get("cons", [])

        if summary:
            lines += ["", "📝 <b>Overview</b>", summary]

        if pros:
            lines += ["", "✅ <b>Pros for Malaysian Riders</b>"]
            for pro in pros:
                lines.append(f"  • {_esc(pro)}")

        if cons:
            lines += ["", "❌ <b>Cons for Malaysian Riders</b>"]
            for con in cons:
                lines.append(f"  • {_esc(con)}")
    else:
        lines += ["", "⚠️ Analysis unavailable at this time."]

    lines += [
        "",
        "─────────────────────",
        "🤖 <i>Malaysia Moto Bot • Powered by AI</i>",
    ]

    return "\n".join(lines)


def _esc(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parse mode."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def send_launch_update(article: dict, analysis: Optional[dict]) -> bool:
    """Convenience wrapper: format and send a single launch update."""
    message = format_launch_message(article, analysis)
    return send_message(message)


def send_status_message(text: str) -> bool:
    """Send a plain status/info message (no HTML formatting)."""
    return send_message(text, parse_mode="HTML")
