"""Flask web app for displaying full YouTube transcripts."""
from __future__ import annotations

from flask import Flask, Response, render_template, request
from jinja2 import TemplateNotFound

from short_movie_generator.summary import format_timestamp
from short_movie_generator.transcript import (
    TranscriptFetcher,
    TranscriptLine,
    video_id_from_url,
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.jinja_env.globals["format_timestamp"] = format_timestamp

    def _render_index(
        *,
        error: str | None = None,
        transcript: list[TranscriptLine] | None = None,
        video_url: str = "",
        video_id: str | None = None,
        languages_input: str = "ja en",
        status: int = 200,
    ) -> Response:
        try:
            return Response(
                render_template(
                    "index.html",
                    transcript=transcript,
                    error=error,
                    video_url=video_url,
                    video_id=video_id,
                    languages_input=languages_input,
                ),
                status=status,
            )
        except TemplateNotFound:
            # If the template cannot be resolved (e.g. when running from a
            # different working directory), return a minimal fallback page so
            # the request does not fail with a 500 response.
            fallback_lines = ["字幕がありません。"]
            if transcript:
                fallback_lines = [f"{format_timestamp(line.start)} {line.text}" for line in transcript]
            fallback_message = error or "ページを表示できませんでした。"
            fallback = "\n".join(
                [
                    "<!doctype html>",
                    "<html lang=\"ja\">",
                    "<meta charset=\"utf-8\">",
                    "<title>YouTube字幕を表示</title>",
                    f"<p>{fallback_message}</p>",
                    "<div>",
                    *[f"<p>{item}</p>" for item in fallback_lines],
                    "</div>",
                ]
            )
            return Response(fallback, status=status, mimetype="text/html")

    @app.route("/", methods=["GET", "POST"])
    def index():
        error: str | None = None
        transcript: list[TranscriptLine] | None = None
        video_url = request.form.get("video_url", "") if request.method == "POST" else ""
        languages_input = request.form.get("languages", "ja en") if request.method == "POST" else "ja en"
        languages = [lang.strip() for lang in languages_input.split() if lang.strip()] or ["ja", "en"]
        video_id: str | None = None

        if request.method == "POST":
            try:
                video_id = video_id_from_url(video_url)
                fetcher = TranscriptFetcher(language_preference=languages)
                transcript = fetcher.fetch(video_id)
            except ValueError as exc:
                error = str(exc) or "動画の処理中にエラーが発生しました。"
            except Exception:
                app.logger.exception("Unexpected error while handling request")
                error = "予期しないエラーが発生しました。時間をおいて再試行してください。"

        return _render_index(
            transcript=transcript,
            error=error,
            video_url=video_url,
            video_id=video_id,
            languages_input=" ".join(languages),
        )

    @app.errorhandler(Exception)
    def handle_global_error(error: Exception):  # noqa: ANN001
        app.logger.exception("Unhandled error", exc_info=error)
        return _render_index(
            error="予期しないエラーが発生しました。時間をおいて再試行してください。",
            status=500,
        )

    return app


app = create_app()
