import datetime
from collections import Counter

import pytest
import matplotlib.pyplot as plt

from cock_size.cocksize import render_cock_size_text, get_cock_size_text, get_cock_size
from plubot.config import config


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
    config.extra['seed_secret'] = 'seed'
    assert get_cock_size_text(1234).startswith("My cock size is ")


def test_get_cock_size_template_and_max_size():
    config.extra['seed_secret'] = 'seed'
    assert get_cock_size_text(1234,
                              template='My clitoris size is {size}cm {emoji}',
                              min_size=0,
                              max_size=10,
                              ).startswith("My clitoris size is ")


def test_get_cock_size_seed():
    config.extra['seed_secret'] = 'seed'
    assert get_cock_size_text(296279045) != get_cock_size_text(296279060)
    assert get_cock_size_text(296279034) != get_cock_size_text(296279023)
    assert get_cock_size_text(1) == get_cock_size_text(1)


def test_get_cock_size_countes():
    start_dt = datetime.date(2022, 1, 1)
    c = Counter()
    sizes = []
    for d in range(365):
        dt = (start_dt + datetime.timedelta(days=d)).isoformat()
        seed = f'{dt}-296279045'
        size = get_cock_size(seed, min_size=1, max_size=100)
        sizes.append(size)
        c[size] += 1
    c = sorted(c.items())
    assert c
    plt.hist(sizes, bins=200)
    plt.show()
