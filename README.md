# 🏍️ Malaysia Motorcycle Launch Bot

A Python bot that automatically fetches the **latest motorcycle launches in Malaysia**, analyses each bike's **pros and cons for the Malaysian market** using AI, and sends formatted updates straight to your **Telegram** chat.

---

## Features

| Feature | Details |
|---|---|
| 📰 News scraping | BikesRepublic, Wapcar.my, Paultan.org |
| 🤖 AI analysis | OpenAI (GPT-4o-mini by default) generates Malaysia-specific pros & cons |
| 📲 Telegram delivery | Formatted HTML messages via Telegram Bot API |
| ⏰ Scheduling | Runs daily at a configurable time |
| 🔁 One-shot mode | `--once` flag for use with system cron |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- A [Telegram Bot token](https://core.telegram.org/bots#botfather) and your chat ID
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ✅ | Your chat/group/channel ID (use [@userinfobot](https://t.me/userinfobot)) |
| `OPENAI_API_KEY` | ✅ | Key from [platform.openai.com](https://platform.openai.com/api-keys) |
| `OPENAI_MODEL` | ❌ | Model to use (default: `gpt-4o-mini`) |
| `ARTICLES_PER_SOURCE` | ❌ | Articles per news source (default: `5`) |
| `SCHEDULE_TIME` | ❌ | Daily run time e.g. `08:00` (server local time, default: `08:00`) |
| `RUN_ON_START` | ❌ | Run immediately on startup (`1`/`0`, default: `1`) |

### 4. Test your setup

```bash
python bot.py --test
```

You should receive a test message in your Telegram chat.

### 5. Run the bot

```bash
# Continuous mode – runs on schedule (default: 08:00 daily)
python bot.py

# One-shot mode – run once and exit (great for cron jobs)
python bot.py --once
```

---

## Example Telegram Message

```
🏍️ Malaysia Motorcycle Launch Update

📰 Honda CB500F launched in Malaysia at RM29,888
🔗 Read full article — BikesRepublic

📝 Overview
A capable middleweight naked bike that fits well within the Malaysian B2 licence
category. Its 471 cc parallel-twin offers a good balance of city commuting and
weekend touring potential.

✅ Pros for Malaysian Riders
  • Fuel-efficient engine (~25 km/L) — affordable to run given RON95 prices
  • Abundant Honda service centres across Malaysia
  • Manageable weight (189 kg) for urban stop-and-go traffic
  • A2-class power output suits newer riders upgrading from 150 cc bikes

❌ Cons for Malaysian Riders
  • Price point above budget-conscious buyers who prefer Modenas/Honda Wave
  • Upright seating may cause fatigue on long highway stretches
  • Limited underseat storage for daily commuters

─────────────────────
🤖 Malaysia Moto Bot • Powered by AI
```

---

## Running with Cron (alternative to built-in scheduler)

```cron
# Every day at 8:00 AM Malaysia Time (UTC+8 = 00:00 UTC)
0 0 * * * cd /path/to/shiny-lamp && /usr/bin/python bot.py --once >> /var/log/moto_bot.log 2>&1
```

---

## Project Structure

```
.
├── bot.py               # Main entry point & scheduler
├── scraper.py           # Web scraping from Malaysian motorcycle news sites
├── analyzer.py          # OpenAI-powered pros/cons analysis
├── telegram_sender.py   # Telegram Bot API integration
├── config.py            # Environment variable configuration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── tests/
    ├── test_scraper.py
    ├── test_analyzer.py
    └── test_telegram_sender.py
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Notes

- The bot scrapes publicly available news pages. If a site changes its HTML structure, the scraper selector in `scraper.py` may need updating.
- OpenAI API costs are minimal when using `gpt-4o-mini` (~$0.001 per analysis).
- The `.env` file is **never** committed (see `.gitignore`).
