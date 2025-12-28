"""Helpers for fetching and preparing YouTube transcripts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
    from youtube_transcript_api._errors import (  # type: ignore
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )


@dataclass
class TranscriptLine:
    """A single line of transcript text."""

    text: str
    start: float


class TranscriptFetcher:
    """Fetch and normalize transcripts from YouTube."""

    def __init__(self, language_preference: Optional[List[str]] = None) -> None:
        self.language_preference = language_preference or ["ja", "en"]

    def fetch(self, video_id: str) -> List[TranscriptLine]:
        """Return transcript lines for a video.

        Raises a ValueError with a user-friendly message when the transcript
        cannot be obtained.
        """

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import (
                NoTranscriptFound,
                TranscriptsDisabled,
                VideoUnavailable,
            )
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise ValueError(
                "youtube-transcript-api がインストールされていません。\n"
                "pip install -r requirements.txt を実行して依存関係を用意してください。"
            ) from exc

        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=self.language_preference
            )
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as exc:
            message = (
                "この動画の字幕を取得できませんでした。字幕が無効化されているか、"
                "対応する言語の字幕が存在しません。"
            )
            raise ValueError(message) from exc
        except Exception as exc:
            raise ValueError(
                "字幕の取得中にエラーが発生しました。動画が非公開/地域・年齢制限付きであるか、"
                "ネットワークに問題がある可能性があります。公開設定を確認し、字幕の言語を変更するか、"
                "ネットワーク状態を確認してから再度お試しください。"
                f" (技術的な詳細: {exc})"
            ) from exc

        return [TranscriptLine(text=item["text"].strip(), start=item["start"]) for item in transcript]


def video_id_from_url(url: str) -> str:
    """Extract the YouTube video ID from a URL or ID string.

    Accepts typical YouTube formats such as full URLs, shortened URLs, or raw
    IDs. Raises ValueError when no ID can be extracted.
    """

    candidate = url.strip()

    # If the candidate already looks like an ID (11 chars without URL markers),
    # accept it directly.
    if re.fullmatch(r"[\w-]{11}", candidate):
        return candidate

    patterns: Iterable[str] = [
        r"(?:v=)([\w-]{11})",  # standard URL query parameter
        r"youtu\.be/([\w-]{11})",  # shortened URL
        r"/embed/([\w-]{11})",  # embed URL
    ]

    for pattern in patterns:
        match = re.search(pattern, candidate)
        if match:
            return match.group(1)

    raise ValueError("有効なYouTubeのURLまたは動画IDを指定してください。")
