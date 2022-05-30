import pluggy
from telegram import Update
from telegram.ext import Dispatcher, CallbackContext

from plubot.plugin import hook_types

hookspec = pluggy.HookspecMarker("plubot")


@hookspec
def prepare_bot(dp: Dispatcher):
    """
    A low level bot preparation

    https://docs.python-telegram-bot.org/en/v13.11/telegram.ext.dispatcher.html
    """
    pass


@hookspec
def inline_query(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:
    """
    No use update.inline_query.answer!
    """


@hookspec
def commands() -> hook_types.HookCommandsReturnType:
    pass


@hookspec
def commands_info() -> hook_types.HookCommandsInfoReturnType:
    pass


@hookspec
def commands_help(
    update: Update, context: CallbackContext
) -> hook_types.HookCommandsHelpReturnType:
    pass


@hookspec
def bot_data_class() -> hook_types.HookChatDataClassReturnType:
    pass


@hookspec
def chat_data_class() -> hook_types.HookChatDataClassReturnType:
    pass


@hookspec
def user_data_class() -> hook_types.HookChatDataClassReturnType:
    pass


@hookspec
def context_class() -> hook_types.HookChatDataClassReturnType:
    pass
