from short_movie_generator.summary import format_timestamp


def test_format_timestamp():
    assert format_timestamp(0) == "00:00"
    assert format_timestamp(61) == "01:01"
