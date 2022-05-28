from plubot.config import config


def test_extra():
    config.extra = {}
    config.extra['attr'] = 'foo'
    assert config.attr == 'foo'
