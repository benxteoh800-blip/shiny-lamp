"""
tests/test_telegram_sender.py – Unit tests for the telegram_sender module.
"""

from unittest.mock import MagicMock, patch

from telegram_sender import _split_message, format_launch_message, _esc


class TestSplitMessage:
    def test_short_message_unchanged(self):
        text = "Hello, world!"
        assert _split_message(text, 100) == [text]

    def test_long_message_split_at_newline(self):
        text = "A\n" * 50  # 100 chars
        chunks = _split_message(text, 30)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 30

    def test_long_message_no_newline(self):
        text = "x" * 200
        chunks = _split_message(text, 100)
        assert len(chunks) == 2
        assert all(len(c) <= 100 for c in chunks)


class TestEscape:
    def test_escapes_ampersand(self):
        assert _esc("Rock & Roll") == "Rock &amp; Roll"

    def test_escapes_lt_gt(self):
        assert _esc("<b>bold</b>") == "&lt;b&gt;bold&lt;/b&gt;"

    def test_no_special_chars(self):
        assert _esc("Hello World") == "Hello World"


class TestFormatLaunchMessage:
    def _sample_article(self):
        return {
            "title": "Honda CB500F launched in Malaysia",
            "url": "https://www.bikesrepublic.com/test",
            "source": "BikesRepublic",
            "bike_name": "Honda CB500F",
            "fetched_at": "2024-01-01T00:00:00",
        }

    def _sample_analysis(self):
        return {
            "pros": ["Good fuel efficiency", "Easy to maintain"],
            "cons": ["Heavy for city traffic"],
            "summary": "A solid mid-range bike for Malaysian riders.",
        }

    def test_contains_title(self):
        msg = format_launch_message(self._sample_article(), self._sample_analysis())
        assert "Honda CB500F" in msg

    def test_contains_pros(self):
        msg = format_launch_message(self._sample_article(), self._sample_analysis())
        assert "Good fuel efficiency" in msg

    def test_contains_cons(self):
        msg = format_launch_message(self._sample_article(), self._sample_analysis())
        assert "Heavy for city traffic" in msg

    def test_contains_summary(self):
        msg = format_launch_message(self._sample_article(), self._sample_analysis())
        assert "solid mid-range bike" in msg

    def test_no_analysis_shows_warning(self):
        msg = format_launch_message(self._sample_article(), None)
        assert "Analysis unavailable" in msg

    def test_contains_article_url(self):
        msg = format_launch_message(self._sample_article(), None)
        assert "https://www.bikesrepublic.com/test" in msg
