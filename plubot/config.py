import sys

import pluggy

TOKEN = '972195986:AAEFhkerwp8HmNDP-XlSNUcPrKG-eX37Oa4'
REQUEST_KWARGS = {
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
    'proxy_url': 'http://localhost:8118/',
}

# Plugins
hookspec = pluggy.HookspecMarker("plubot")
hookimpl = pluggy.HookimplMarker("plubot")

sys.path.insert(0,
                "/home/apkawa/code/python-meme-generator")
