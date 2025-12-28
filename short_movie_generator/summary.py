"""Summarization and key line extraction for transcripts."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .transcript import TranscriptLine

# Basic stop words for scoring.
STOPWORDS = {
    "the",
    "a",
    "an",
    "to",
    "and",
    "or",
    "is",
    "are",
    "was",
    "were",
    "of",
    "in",
    "on",
    "for",
    "with",
    "that",
    "this",
    "it",
    "as",
    "at",
    "be",
    "by",
    "from",
    "we",
    "you",
    "i",
    "me",
    "my",
    "our",
    "us",
}


def _tokenize(text: str) -> List[str]:
    return [token for token in re.split(r"[^\w']+", text.lower()) if token]


def _score_sentences(lines: Sequence[TranscriptLine]) -> List[float]:
    """Score sentences based on word frequency and positional emphasis."""

    all_tokens: Iterable[str] = (
        token for line in lines for token in _tokenize(line.text) if token not in STOPWORDS
    )
    frequencies = Counter(all_tokens)
    if not frequencies:
        return [0.0 for _ in lines]

    max_freq = max(frequencies.values())
    normalized = {word: freq / max_freq for word, freq in frequencies.items()}

    scores: List[float] = []
    total_lines = len(lines)

    for index, line in enumerate(lines):
        tokens = [token for token in _tokenize(line.text) if token not in STOPWORDS]
        base_score = sum(normalized.get(token, 0.0) for token in tokens)

        # Slightly favor earlier sentences for introductory importance.
        positional_boost = (total_lines - index) / total_lines
        scores.append(base_score * positional_boost)

    return scores


def _top_keywords(text: str, top_k: int = 3) -> List[str]:
    tokens = [token for token in _tokenize(text) if token not in STOPWORDS]
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(top_k)]


def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(math.floor(seconds % 60))
    return f"{minutes:02d}:{secs:02d}"


@dataclass
class KeyLine:
    line: TranscriptLine
    explanation: str


class KeyLineExtractor:
    """Identify the most representative lines from a transcript."""

    def __init__(self, lines: Sequence[TranscriptLine]):
        self.lines = list(lines)

    def extract(self, count: int = 3) -> List[KeyLine]:
        if not self.lines:
            return []

        scores = _score_sentences(self.lines)
        scored_lines = list(zip(self.lines, scores))
        scored_lines.sort(key=lambda item: item[1], reverse=True)

        selected: List[KeyLine] = []
        used_indices = set()

        for line, _ in scored_lines:
            idx = self.lines.index(line)
            if idx in used_indices:
                continue
            used_indices.add(idx)

            explanation = self._build_explanation(idx)
            selected.append(KeyLine(line=line, explanation=explanation))

            if len(selected) >= count:
                break

        return selected

    def _build_explanation(self, index: int) -> str:
        line = self.lines[index]
        keywords = _top_keywords(line.text)
        keyword_hint = (
            f"キーワード: {', '.join(keywords)}" if keywords else "キーワード情報はありません"
        )

        context = self._neighboring_text(index)
        timestamp = format_timestamp(line.start)
        return f"{timestamp}頃のセリフ。{context} {keyword_hint}。"

    def _neighboring_text(self, index: int, window: int = 1) -> str:
        start = max(index - window, 0)
        end = min(index + window + 1, len(self.lines))
        neighbors = [self.lines[i].text for i in range(start, end) if i != index]
        if not neighbors:
            return "前後の文脈はありません。"
        joined = " / ".join(neighbors)
        return f"前後の文脈: {joined}" 
