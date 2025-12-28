import pytest

pytest.importorskip("flask")

from short_movie_generator.web_app import create_app
from short_movie_generator.transcript import TranscriptLine
from jinja2 import TemplateNotFound


def test_web_app_displays_transcript(monkeypatch):
    app = create_app()
    client = app.test_client()

    class DummyFetcher:  # pragma: no cover - exercised through request
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

        def fetch(self, video_id):  # noqa: ARG002
            return [TranscriptLine(text="Hello", start=0.0), TranscriptLine(text="World", start=5.0)]

    monkeypatch.setattr("short_movie_generator.web_app.TranscriptFetcher", DummyFetcher)

    response = client.post(
        "/",
        data={"video_url": "https://youtu.be/dQw4w9WgXcQ", "languages": "ja"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Hello" in body and "World" in body
    assert "00:00" in body and "00:05" in body
    assert "href=\"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=5s\"" in body


def test_web_app_handles_unexpected_errors(monkeypatch):
    app = create_app()
    client = app.test_client()

    class FailingFetcher:  # pragma: no cover - exercised through request
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            pass

        def fetch(self, video_id):  # noqa: ARG002
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "short_movie_generator.web_app.TranscriptFetcher", FailingFetcher
    )

    response = client.post(
        "/",
        data={"video_url": "https://youtu.be/dQw4w9WgXcQ", "languages": "ja"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "予期しないエラー" in body


def test_web_app_renders_fallback_when_template_missing(monkeypatch):
    app = create_app()
    client = app.test_client()

    # Force template rendering to fail to ensure the handler still returns a response.
    monkeypatch.setattr(
        "short_movie_generator.web_app.render_template",
        lambda *args, **kwargs: (_ for _ in ()).throw(TemplateNotFound("index.html")),
    )

    response = client.get("/")

    assert response.status_code == 200
    assert "ページを表示できませんでした" in response.get_data(as_text=True)
