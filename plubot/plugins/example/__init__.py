from typing import Tuple, Callable, List

from telegram import InlineQueryResult
from telegram.ext import Dispatcher

from plubot.config import hookimpl


@hookimpl
def prepare_bot(dp: Dispatcher) -> None:
    pass


@hookimpl
def inline_query_cmd_handler() -> Tuple[str, Callable[[str], List[InlineQueryResult]]]:
    '''
    Example command
    '''
