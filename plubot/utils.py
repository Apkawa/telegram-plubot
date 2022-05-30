from typing import Union
from types import ModuleType
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from uuid import uuid4

from telegram.ext import CallbackContext


def import_from_path(path: Union[str, Path]) -> ModuleType:
    path = Path(path)

    if path.is_dir():
        path = path / "__init__.py"

    module_name = path.parent.name

    spec = spec_from_file_location(module_name, path)
    if spec:
        module = module_from_spec(spec)
    else:
        raise ImportError(f"No spec module {module_name} {path}")
    return module


def gen_id() -> str:
    return str(uuid4())


def remove_jobs(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
