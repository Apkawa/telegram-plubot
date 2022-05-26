from telegram import Update
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from plubot.plugin import hook_types, hookimpl

from . import simple_inlinekeyboard, context_types

# Plugins decomposition
PLUGINS = [simple_inlinekeyboard, context_types]
# More examples
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v13.11/examples


@hookimpl
def prepare_bot(dp: Dispatcher) -> None:
    pass


def foo_cmd(update: Update, context: CallbackContext):
    """
    foo is foo command
    """
    update.message and update.message.reply_text(f"Foo command execute with args {context.args}")


# Use chat data instead
MESSAGE_REPLY = {}


def bar_cmd(update: Update, context: CallbackContext):
    """
    bar is bar command
    """
    text = f"Bar command execute with args {context.args}"
    if update.message:
        message = update.message.reply_text(text)
        MESSAGE_REPLY[update.message.message_id] = message.message_id
    elif update.edited_message:
        bot_message_id = MESSAGE_REPLY[update.edited_message.message_id]
        context.bot.edit_message_text(
            text,
            chat_id=update.edited_message.chat_id,
            message_id=bot_message_id,
        )


@hookimpl
def commands() -> hook_types.HookCommandsReturnType:
    return {
        "foo": foo_cmd,
        "bar": CommandHandler("bar", bar_cmd, pass_args=True),
    }


@hookimpl
def commands_help(
    update: Update, context: CallbackContext
) -> hook_types.HookCommandsHelpReturnType:
    # Maybe acl
    user = update.effective_user
    if not user:
        return None
    return f"""
    /foo - is foo command
        /bar - is bar command

            You is {user.name} [{user.id}]
    """
