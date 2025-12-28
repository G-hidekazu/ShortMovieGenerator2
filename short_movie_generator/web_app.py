"""Flask web app for extracting key lines from YouTube transcripts."""
from __future__ import annotations

from flask import Flask, render_template, request

from .summary import KeyLineExtractor, format_timestamp
from .transcript import TranscriptFetcher, video_id_from_url


def create_app() -> Flask:
    app = Flask(__name__)
    app.jinja_env.globals["format_timestamp"] = format_timestamp
    @app.route("/", methods=["GET", "POST"])
    def index():
        error: str | None = None
        results = None
        video_url = request.form.get("video_url", "") if request.method == "POST" else ""
        languages_input = request.form.get("languages", "ja en") if request.method == "POST" else "ja en"
        languages = [lang.strip() for lang in languages_input.split() if lang.strip()] or ["ja", "en"]

        if request.method == "POST":
            try:
                video_id = video_id_from_url(video_url)
                fetcher = TranscriptFetcher(language_preference=languages)
                lines = fetcher.fetch(video_id)
                extractor = KeyLineExtractor(lines)
                results = extractor.extract()
            except ValueError as exc:
                error = str(exc) or "動画の処理中にエラーが発生しました。"

        return render_template(
            "index.html",
            results=results,
            error=error,
            video_url=video_url,
            languages_input=" ".join(languages),
        )

    return app


app = create_app()
