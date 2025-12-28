import sys
import types

import pytest

from short_movie_generator.transcript import TranscriptFetcher


def test_fetch_wraps_unexpected_errors(monkeypatch):
    api_module = types.ModuleType("youtube_transcript_api")

    class DummyApi:  # pragma: no cover - behavior exercised through fetcher
        @staticmethod
        def get_transcript(video_id, languages=None):  # noqa: ARG002
            raise RuntimeError("network down")

    api_module.YouTubeTranscriptApi = DummyApi

    errors_module = types.ModuleType("youtube_transcript_api._errors")

    class DummyError(Exception):
        pass

    errors_module.NoTranscriptFound = DummyError
    errors_module.TranscriptsDisabled = DummyError
    errors_module.VideoUnavailable = DummyError

    monkeypatch.setitem(sys.modules, "youtube_transcript_api", api_module)
    monkeypatch.setitem(sys.modules, "youtube_transcript_api._errors", errors_module)

    fetcher = TranscriptFetcher()

    with pytest.raises(ValueError) as excinfo:
        fetcher.fetch("abcdefghijk")

    assert "予期しないエラー" in str(excinfo.value)
