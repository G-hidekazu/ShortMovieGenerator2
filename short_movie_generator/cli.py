"""Command-line interface for extracting key quotes from a YouTube video."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .summary import KeyLineExtractor
from .transcript import TranscriptFetcher, video_id_from_url


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YouTube動画から重要な3つのセリフと解説を抽出します。"
    )
    parser.add_argument("url", help="YouTubeの動画URLまたは動画ID")
    parser.add_argument(
        "--lang",
        nargs="+",
        dest="languages",
        default=["ja", "en"],
        help="字幕取得で優先する言語（複数指定可、デフォルト: ja en）",
    )
    return parser.parse_args(args)


def main(argv: List[str] | None = None) -> int:
    options = parse_args(argv or sys.argv[1:])
    try:
        video_id = video_id_from_url(options.url)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    fetcher = TranscriptFetcher(language_preference=options.languages)
    try:
        transcript = fetcher.fetch(video_id)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    extractor = KeyLineExtractor(transcript)
    key_lines = extractor.extract()

    if not key_lines:
        print("字幕が空のため、セリフを抽出できませんでした。", file=sys.stderr)
        return 1

    print("=== 重要なセリフと解説 ===")
    for idx, key_line in enumerate(key_lines, start=1):
        print(f"{idx}. {key_line.line.text}")
        print(f"   -> {key_line.explanation}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
