import pytest

from example_bot.plugins.cocksize import render_cock_size_text, get_cock_size_text


@pytest.mark.parametrize(
    "size,text",
    [
        [1, "My cock size is 1cm 😭"],
        [10, "My cock size is 10cm 🙁"],
        [42, "My cock size is 42cm 😎"],
    ],
)
def test_render_cock_size(size, text):
    assert render_cock_size_text(size) == text


def test_get_cock_size():
    assert get_cock_size_text(1234).startswith("My cock size is ")
