import pytest

pytest.importorskip("flask")

from short_movie_generator.web_app import create_app


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
