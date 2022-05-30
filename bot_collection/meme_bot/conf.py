import os

from . import meme

TOKEN = os.environ.get("TOKEN")

PROXY = None

PLUGINS = [
    meme
]
