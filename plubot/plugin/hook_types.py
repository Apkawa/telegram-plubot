from typing import Union, List, Dict, Callable, Type, Optional, TypeVar, Tuple
from typing_extensions import TypeAlias

from telegram import InlineQueryResult, Update, BotCommand
from telegram.ext import CallbackContext, Handler

from plubot.bot_command import BotCommandInfo

InlineQueryResultType = TypeVar('InlineQueryResultType', bound=InlineQueryResult)

HookInlineQueryReturnType: TypeAlias = Optional[Union[str, List[InlineQueryResultType]]]

GenericHandlerCallback: TypeAlias = Callable[[Update, CallbackContext], None]

HookCommandsReturnType: TypeAlias = Dict[
    str,
    Union[
        GenericHandlerCallback, Handler, List[Union[GenericHandlerCallback, Handler]]
    ],
]

HookCommandsInfoReturnType: TypeAlias = List[
    Union[
        Tuple[str, str],
        BotCommandInfo,
    ]
]

HookCommandsHelpReturnType: TypeAlias = Union[str, None]

HookBotDataClassReturnType: TypeAlias = Optional[Type]
HookChatDataClassReturnType: TypeAlias = Optional[Type]
HookUserDataClassReturnType: TypeAlias = Optional[Type]

HootContextClassReturnType: TypeAlias = Optional[
    Type[CallbackContext[dict, Type, dict]]
]
