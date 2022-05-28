from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, \
    BotCommandScopeAllPrivateChats, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler

from plubot.bot_command import BotCommandInfo
from plubot.plugin import hookimpl, hook_types


def button_cmd(update: Update, context: CallbackContext):
    """
    foo is foo command
    """
    keyboard = [
        ['+', '-', '0']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)
    update.effective_message.reply_text("Current number: 0",
                                        reply_markup=reply_markup)




@hookimpl
def commands() -> hook_types.HookCommandsReturnType:

    return {
        "calc": [
            button_cmd,
        ]
    }


@hookimpl
def commands_help(
    update: Update, context: CallbackContext
) -> hook_types.HookCommandsHelpReturnType:
    return """
    /calc - example inline keyboard
    """


@hookimpl
def commands_info() -> hook_types.HookCommandsInfoReturnType:
    return [
        BotCommandInfo('calc', 'example reply keyboard',
                       scope=BotCommandScopeAllPrivateChats())
    ]
