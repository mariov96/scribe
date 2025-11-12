"""Utility helpers for AI-style transcription cleanup."""
from __future__ import annotations

import re
from typing import Optional

from scribe.config.models import AIFormattingConfig


class TextFormatter:
    """Apply light-weight AI-style cleanup without external APIs."""

    _FILLER_WORDS = {
        "um",
        "uh",
        "erm",
        "hmm",
        "like",
        "kind of",
        "sort of",
    }

    _VOICE_REPLACEMENTS = [
        (r"\bnew paragraph\b", "\n\n"),
        (r"\bnext paragraph\b", "\n\n"),
        (r"\bnew line\b", "\n"),
        (r"\bline break\b", "\n"),
        (r"\bbullet point\b", "\n• "),
        (r"\bnext bullet\b", "\n• "),
        (r"\bbullet\b", "\n• "),
    ]

    _NUMBER_WORDS = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    _QUESTION_STARTERS = (
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "did",
        "do",
        "does",
        "can",
        "will",
        "should",
        "is",
        "are",
    )

    def __init__(self, config: AIFormattingConfig):
        self.config = config

    def update_config(self, config: AIFormattingConfig):
        self.config = config

    def format_text(self, text: str) -> str:
        processed = (text or "").strip()
        if not processed:
            return processed

        if self.config.enable_ai_cleanup:
            processed = self._remove_fillers(processed)

        if self.config.enable_voice_commands:
            processed = self._apply_voice_commands(processed)

        if self.config.enable_number_conversion:
            processed = self._convert_numbers(processed)

        if self.config.enable_smart_punctuation:
            processed = self._smart_punctuation(processed)

        processed = self._normalize_whitespace(processed)

        if self.config.phantom_recording_protection and len(processed.split()) <= 1:
            return processed.strip()

        return processed.strip()

    # --- helpers ---------------------------------------------------------

    def _remove_fillers(self, text: str) -> str:
        pattern = re.compile(r"\b(" + "|".join(re.escape(w) for w in self._FILLER_WORDS) + r")\b", re.IGNORECASE)
        cleaned = pattern.sub("", text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def _apply_voice_commands(self, text: str) -> str:
        processed = text
        for pattern, replacement in self._VOICE_REPLACEMENTS:
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
        return processed

    def _convert_numbers(self, text: str) -> str:
        pattern = re.compile(r"\b(" + "|".join(self._NUMBER_WORDS.keys()) + r")\b", re.IGNORECASE)
        return pattern.sub(lambda m: self._NUMBER_WORDS[m.group(0).lower()], text)

    def _smart_punctuation(self, text: str) -> str:
        text = text.strip()
        if not text:
            return text
        if text[-1] in ".?!":
            return text
        lower = text.lower()
        if lower.startswith(self._QUESTION_STARTERS):
            return text + "?"
        return text + "."

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        text = re.sub(r"\s*\n\s*", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text
