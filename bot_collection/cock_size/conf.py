import os
from . import cocksize

TOKEN = os.environ.get("TOKEN")
SEED_SECRET = os.environ.get("SEED_SECRET")

PROXY = None

PLUGINS = [
    cocksize
]
