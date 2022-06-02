from pathlib import Path

from .utils import CleanablePath


def test_cleanable_path():
    c = CleanablePath('/tmp/fake_path')
    assert not c.exists()
    assert not c.remove()
    del c

    real_path = Path('/tmp/real_path.txt')
    open(real_path, 'w').write('1')
    assert real_path.exists()
    c = CleanablePath(real_path)
    assert c.exists()
    del c
    assert not real_path.exists()

    real_path = Path('/tmp/real_path.txt')

    open(real_path, 'w').write('1')
    assert real_path.exists()

    def _f():
        c = CleanablePath(real_path)
        assert c.exists()

    _f()
    assert not real_path.exists()
