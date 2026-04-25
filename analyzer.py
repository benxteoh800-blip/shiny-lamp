"""
analyzer.py – Uses the OpenAI API to generate Malaysia-specific pros and cons
               for a given motorcycle model.
"""

import logging
from typing import Optional

import openai

from config import Config

logger = logging.getLogger(__name__)


_MALAYSIA_CONTEXT = """
You are a motorcycle expert who knows the Malaysian market very well.
Malaysia has:
- Hot and humid tropical climate (28–35 °C year-round, heavy rain during monsoon).
- Dense urban traffic in KL and other cities; moderate rural roads.
- Fuel prices are government-subsidised (RON95 is common).
- Motorcycle culture is very strong; bikes are a primary mode of transport.
- Popular brands: Honda, Yamaha, Kawasaki, Suzuki, Modenas (local brand).
- Spare-parts availability varies by brand popularity.
- Most buyers are price-sensitive; monthly instalments are common.
- Road conditions range from excellent highways to potholed rural roads.
- Motorcycles above 250 cc require a B2 full licence.
"""


def analyze_motorcycle(article: dict) -> Optional[dict]:
    """
    Query OpenAI to produce pros/cons of the motorcycle for the Malaysian market.

    Args:
        article: dict with at least 'bike_name' and 'title' keys.

    Returns:
        dict with keys 'pros', 'cons', 'summary', or None on failure.
    """
    bike_name = article.get("bike_name") or article.get("title", "Unknown motorcycle")

    prompt = f"""
{_MALAYSIA_CONTEXT}

A new motorcycle has been launched or is being discussed in Malaysia:
"{bike_name}"

Please provide:
1. **Pros** (at least 4 bullet points) – advantages of this bike for Malaysian riders.
2. **Cons** (at least 3 bullet points) – disadvantages or concerns for Malaysian riders.
3. **Summary** (2–3 sentences) – overall verdict for the Malaysian market.

Be specific. Mention factors like price, fuel consumption, heat management,
parts availability, licence requirements, and suitability for Malaysian roads.
Keep the language concise and easy to read.
"""

    try:
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful automotive journalist specialising in "
                        "the Malaysian motorcycle market. Respond in clear, friendly English."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        raw_text = response.choices[0].message.content.strip()
        return _parse_analysis(raw_text)

    except openai.OpenAIError as exc:
        logger.error("OpenAI API error for '%s': %s", bike_name, exc)
        return None


def _parse_analysis(raw_text: str) -> dict:
    """
    Parse the raw OpenAI response into structured pros / cons / summary.
    Falls back gracefully if the model's format is unexpected.
    """
    sections = {"pros": [], "cons": [], "summary": ""}

    current_section = None
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if "pros" in lower and ("**" in line or line.endswith(":")):
            current_section = "pros"
        elif "cons" in lower and ("**" in line or line.endswith(":")):
            current_section = "cons"
        elif "summary" in lower and ("**" in line or line.endswith(":")):
            current_section = "summary"
        elif current_section in ("pros", "cons") and line.startswith(("•", "-", "*", "1", "2", "3", "4", "5")):
            clean = line.lstrip("•-*0123456789. ").strip()
            if clean:
                sections[current_section].append(clean)
        elif current_section == "summary":
            sections["summary"] += (" " + line) if sections["summary"] else line

    # If parsing failed, put everything in summary
    if not sections["pros"] and not sections["cons"]:
        sections["summary"] = raw_text

    return sections
