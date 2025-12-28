import pytest

from short_movie_generator.cli import main
from short_movie_generator.transcript import TranscriptLine


def test_cli_outputs_full_transcript(monkeypatch, capsys):
    class DummyFetcher:  # pragma: no cover - exercised through CLI
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

        def fetch(self, video_id):  # noqa: ARG002
            return [TranscriptLine(text="Line one", start=0.0)]

    monkeypatch.setattr("short_movie_generator.cli.TranscriptFetcher", DummyFetcher)

    exit_code = main(["https://youtu.be/dQw4w9WgXcQ"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Line one" in captured.out
    assert "00:00" in captured.out


def test_cli_handles_value_errors(monkeypatch, capsys):
    class FailingFetcher:  # pragma: no cover - exercised through CLI
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

        def fetch(self, video_id):  # noqa: ARG002
            raise ValueError("oops")

    monkeypatch.setattr("short_movie_generator.cli.TranscriptFetcher", FailingFetcher)

    exit_code = main(["https://youtu.be/dQw4w9WgXcQ"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "oops" in captured.err
