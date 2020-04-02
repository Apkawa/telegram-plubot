import pluggy

from plubot.plugins import hookspec, plugins


def get_plugin_manager():
    pm = pluggy.PluginManager("plubot")
    pm.add_hookspecs(hookspec)
    pm.load_setuptools_entrypoints("plubot")
    for p in plugins:
        pm.register(p)
    return pm
