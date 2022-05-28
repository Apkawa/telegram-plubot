import pluggy
from . import hook_specs


def get_plugin_manager():
    pm = pluggy.PluginManager("plubot")
    pm.add_hookspecs(hook_specs)
    pm.load_setuptools_entrypoints("plubot")
    return pm
