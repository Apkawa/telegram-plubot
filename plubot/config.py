from types import ModuleType
from typing import Optional, List, Dict, Any

from importlib import import_module


class Config:
    token: str
    proxy: Optional[str]
    module: ModuleType
    plugins: List[str]

    extra: Dict[str, Any]

    def __init__(self):
        self.extra = {}

    def load(self, base_module: ModuleType):
        self.module = base_module
        m = import_module(base_module.__name__ + ".conf")
        conf_dict = {
            i.lower(): v
            for i, v in m.__dict__.items()
            if not i.startswith("_") and i.isupper()
        }

        for n in ["token", "proxy", "plugins"]:
            setattr(self, n, conf_dict.pop(n))

        self.extra = conf_dict

    def __getattr__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return object.__getattribute__(self, 'extra')[item]
            except KeyError:
                raise AttributeError(item)


config = Config()
