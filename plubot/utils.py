import importlib
import os.path
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Union


def import_from_path(path: Union[str, Path]):
    path = Path(path)
    if path.is_file():
        path = path.parent
    module_name = path.name

    spec = spec_from_file_location(module_name, path / '__init__.py')
    module = module_from_spec(spec)
    return module

