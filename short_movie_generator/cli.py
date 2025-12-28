"""Command-line interface for fetching full YouTube transcripts."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .summary import format_timestamp
from .transcript import TranscriptFetcher, video_id_from_url


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YouTube動画の字幕全文を取得して表示します。"
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

    if not transcript:
        print("字幕が空のため、表示できる内容がありません。", file=sys.stderr)
        return 1

    print("=== 字幕全文 ===")
    for line in transcript:
        print(f"{format_timestamp(line.start)} {line.text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
