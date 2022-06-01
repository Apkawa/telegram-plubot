import ast
import os
from importlib import import_module
from types import ModuleType
from typing import Optional, List, Dict, Any, Union, Mapping


def remap_dict_with_dot_sep(
    d: Union[Mapping, Dict[str, Any]], dot_sep: str = '.') -> Dict[str, Any]:
    """
    >>> remap_dict_with_dot_sep({'k1.k2.k3': 3, 'k1.k2.k4': 4, 'k1.k5': 5})
    {'k1': {'k2': {'k3': 3, 'k4': 4}, 'k5': 5}}
    >>> remap_dict_with_dot_sep({'k1.k2.k3': 3, 'k1.k2': {'k4': 4}, 'k1.k2.k5': 5})
    {'k1': {'k2': {'k3': 3, 'k4': 4, 'k5': 5}}}

    # Undefined behavior, no handle case
    >>> remap_dict_with_dot_sep({'k1.k2.k3': 3, 'k1.k2': 2, 'k1.k2.k4': 4})
    Traceback (most recent call last):
    ...
    TypeError: 'int' object does not support item assignment
    """
    res_d = dict(d)
    for k, v in d.items():
        if dot_sep not in k:
            continue
        else:
            s_k, *sub_keys = k.split(dot_sep)
            sub_d = res_d.setdefault(s_k, {})
            sl_k = sub_keys.pop()
            for s_k in sub_keys:
                sub_d = sub_d.setdefault(s_k, {})
            if (isinstance(sub_d, dict)
                and sl_k in sub_d
                and isinstance(sub_d[sl_k], dict)
                and isinstance(v, dict)):
                sub_d[sl_k].update(v)
            else:
                sub_d[sl_k] = v
            del res_d[k]
    return res_d


def get_conf_from_env(env: Union[Mapping, Dict[str, Any]],
                      prefix: str = 'BOT_',
                      dot_sep: str = '.'
                      ) -> Dict[str, Any]:
    """
    collect all env with prefix BOT_

    >>> get_conf_from_env({'BOT_TOKEN': 'token', 'FOO': 'FOO',
    ... 'BOT_KWARGS': "{'foo': 1, 'bar': [2]}"})
    {'token': 'token', 'kwargs': {'foo': 1, 'bar': [2]}}
    >>> get_conf_from_env({'BOT_K1.K2.K3': '3', 'BOT_K1.K4': '4', 'BOT_K5': 5})
    {'k5': 5, 'k1': {'k2': {'k3': 3}, 'k4': 4}}

    # Invalid string structure fallbacked as string
    >>> get_conf_from_env({'BOT_K1': '[foo]', 'BOT_K2': '{foo: 1}]'})
    {'k1': '[foo]', 'k2': '{foo: 1}]'}

    """
    prefix = prefix.lower()
    conf = {}
    for k, v in env.items():
        k = k.lower()
        if not k.startswith(prefix):
            continue
        k = k[len(prefix):]
        try:
            v = ast.literal_eval(v)
        except (SyntaxError, ValueError):
            pass
        conf[k] = v
    conf = remap_dict_with_dot_sep(conf, dot_sep=dot_sep)
    return conf


class Config:
    token: str
    proxy: Optional[str]
    module: ModuleType
    plugins: List[str]

    extra: Dict[str, Any]

    defaults = {
        'proxy': None
    }

    def __init__(self):
        self.extra = {}

    def load(self, base_module: ModuleType):
        self.module = base_module
        m = import_module(base_module.__name__ + ".conf")
        conf_dict = {}
        conf_dict.update(self.defaults)
        conf_file_dict = {
            i.lower(): v
            for i, v in m.__dict__.items()
            if not i.startswith("_") and i.isupper()
        }
        env_conf = get_conf_from_env(os.environ)

        conf_dict.update(conf_file_dict)
        conf_dict.update(env_conf)

        for n in ["token", "proxy", "plugins"]:
            setattr(self, n, conf_dict.pop(n))

        self.extra = conf_dict

    def get(self, key, default=None):
        return self.extra.get(key, default)

    def set(self, key, value):
        self.extra[key] = value

    def __getattr__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return object.__getattribute__(self, 'extra')[item]
            except KeyError:
                raise AttributeError(item)


config = Config()
