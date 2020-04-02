import pluggy

TOKEN = '***REMOVED***'
REQUEST_KWARGS = {
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
    'proxy_url': 'http://localhost:8118/',
}

# Plugins
hookspec = pluggy.HookspecMarker("plubot")
hookimpl = pluggy.HookimplMarker("plubot")

