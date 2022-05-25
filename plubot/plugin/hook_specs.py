import pluggy
from telegram import Update
from telegram.ext import Dispatcher, CallbackContext

from plubot.plugin import hook_types

hookspec = pluggy.HookspecMarker("plubot")


@hookspec
def prepare_bot(dp: Dispatcher):
    pass


@hookspec
def inline_query(query: str, update: Update,
                 context: CallbackContext) -> hook_types.HookInlineQueryReturnType:
    '''
    No use update.inline_query.answer!
    '''


@hookspec
def commands() -> hook_types.HookCommandsReturnType:
    '''

    '''


@hookspec
def help(update: Update,
         context: CallbackContext) -> hook_types.HookCommandsReturnType:
    '''

    '''
