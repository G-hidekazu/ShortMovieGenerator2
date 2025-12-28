from short_movie_generator.summary import KeyLineExtractor, format_timestamp
from short_movie_generator.transcript import TranscriptLine


def test_format_timestamp():
    assert format_timestamp(0) == "00:00"
    assert format_timestamp(61) == "01:01"


def test_key_line_extraction_prefers_scored_lines():
    lines = [
        TranscriptLine(text="Intro to the topic", start=0.0),
        TranscriptLine(text="Deep dive into the important concept", start=10.0),
        TranscriptLine(text="Another filler line", start=20.0),
        TranscriptLine(text="Critical insight about the important concept", start=30.0),
    ]

    extractor = KeyLineExtractor(lines)
    key_lines = extractor.extract()

    assert len(key_lines) == 3
    texts = [item.line.text for item in key_lines]
    assert "important concept" in texts[0].lower()
    assert any("intro" in text.lower() for text in texts)


def test_neighboring_text_in_explanation():
    lines = [
        TranscriptLine(text="Line one", start=0.0),
        TranscriptLine(text="Line two", start=5.0),
        TranscriptLine(text="Line three", start=10.0),
    ]
    extractor = KeyLineExtractor(lines)
    key_lines = extractor.extract(count=1)

    assert key_lines[0].explanation.startswith("00:00") or key_lines[0].explanation.startswith(
        "00:05"
    )
    assert "前後の文脈" in key_lines[0].explanation
