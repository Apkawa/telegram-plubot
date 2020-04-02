from typing import Tuple, Callable, List

from telegram import InlineQueryResult
from telegram.ext import Dispatcher

from plubot.config import hookspec


@hookspec
def prepare_bot(dp: Dispatcher):
    pass


@hookspec
def inline_query_cmd_info() -> Tuple[str, Callable[[str], List[InlineQueryResult]]]:
    '''

    :return: name, callable
    '''
