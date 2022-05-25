from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from plubot.plugin import hook_types, hookimpl


@hookimpl
def prepare_bot(dp: Dispatcher) -> None:
    pass


def foo_cmd(update: Update,
            context: CallbackContext):
    '''
    foo is foo command
    '''
    update.message.reply_text(f'Foo command execute with args {context.args}')


MESSAGE_REPLY = {}


def bar_cmd(update: Update,
            context: CallbackContext):
    '''
    bar is bar command
    '''
    text = f'Bar command execute with args {context.args}'
    if update.message:
        message = update.message.reply_text(text)
        MESSAGE_REPLY[update.message.message_id] = message.message_id
    else:
        bot_message_id = MESSAGE_REPLY[update.effective_message.message_id]
        context.bot.edit_message_text(
            text,
            chat_id=update.effective_message.chat_id,
            message_id=bot_message_id,
        )


@hookimpl
def commands() -> hook_types.HookCommandsReturnType:
    return {
        'foo': foo_cmd,
        'bar': CommandHandler('bar', bar_cmd, pass_args=True),
    }


@hookimpl
def help(update: Update,
         context: CallbackContext) -> hook_types.HookHelpReturnType:
    # Maybe acl
    user = update.effective_user
    return f'''
    /foo - is foo command
        /bar - is bar command

            You is {user.name} [{user.id}]
    '''
