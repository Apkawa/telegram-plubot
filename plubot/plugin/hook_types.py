from typing import Union, List, Dict, Callable, Type, Optional, TypeVar
from typing_extensions import TypeAlias

from telegram import InlineQueryResult, Update
from telegram.ext import CallbackContext, Handler

InlineQueryResultType = TypeVar('InlineQueryResultType', bound=InlineQueryResult)

HookInlineQueryReturnType: TypeAlias = Optional[Union[str, List[InlineQueryResultType]]]

GenericHandlerCallback: TypeAlias = Callable[[Update, CallbackContext], None]

HookCommandsReturnType: TypeAlias = Dict[
    str,
    Union[
        GenericHandlerCallback, Handler, List[Union[GenericHandlerCallback, Handler]]
    ],
]

HookCommandsHelpReturnType: TypeAlias = Union[str, None]

HookChatDataClassReturnType: TypeAlias = Optional[Type]

HootContextClassReturnType: TypeAlias = Optional[
    Type[CallbackContext[dict, Type, dict]]
]
