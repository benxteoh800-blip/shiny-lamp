"""
tests/test_analyzer.py – Unit tests for the analyzer module.
"""

from unittest.mock import MagicMock, patch

from analyzer import _parse_analysis


class TestParseAnalysis:
    def test_parses_pros_cons_summary(self):
        raw = """
**Pros:**
- Great fuel economy
- Affordable price
- Easy to find parts

**Cons:**
- Gets hot in traffic
- Limited seat comfort

**Summary:**
Overall a good choice for Malaysian commuters.
"""
        result = _parse_analysis(raw)
        assert len(result["pros"]) == 3
        assert len(result["cons"]) == 2
        assert "good choice" in result["summary"]

    def test_fallback_on_unparseable_text(self):
        raw = "This is a plain paragraph with no headers."
        result = _parse_analysis(raw)
        assert result["summary"] == raw
        assert result["pros"] == []
        assert result["cons"] == []

    def test_bullet_variations(self):
        raw = """
**Pros:**
• First pro
* Second pro
1. Third pro

**Cons:**
• Only con

**Summary:**
A decent bike.
"""
        result = _parse_analysis(raw)
        assert len(result["pros"]) == 3
        assert len(result["cons"]) == 1
