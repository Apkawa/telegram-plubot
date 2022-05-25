from typing import Union, List, Dict, Callable

from telegram import InlineQueryResult, Update
from telegram.ext import CallbackContext, CommandHandler

HookInlineQueryReturnType = Union[None, str, List[InlineQueryResult]]

GenericHandlerCallback = Callable[[Update, CallbackContext], None]

HookCommandsReturnType = Dict[str, Union[GenericHandlerCallback, CommandHandler]]

HookHelpReturnType = Union[str, None]
