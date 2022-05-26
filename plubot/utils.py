from typing import Union
from types import ModuleType
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from uuid import uuid4


def import_from_path(path: Union[str, Path]) -> ModuleType:
    path = Path(path)
    if path.is_file():
        path = path.parent
    module_name = path.name

    spec = spec_from_file_location(module_name, path / "__init__.py")
    if spec:
        module = module_from_spec(spec)
    else:
        raise ImportError(f"No spec module {module_name} {path}")
    return module


def gen_id() -> str:
    return str(uuid4())
