from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, \
    BotCommandScopeAllPrivateChats
from telegram.ext import CallbackContext, CallbackQueryHandler

from plubot.bot_command import BotCommandInfo
from plubot.plugin import hookimpl, hook_types

keyboard = [
    [
        InlineKeyboardButton("+", callback_data="+"),
        InlineKeyboardButton("-", callback_data="-"),
    ],
    [InlineKeyboardButton("0", callback_data="0")],
]
reply_markup = InlineKeyboardMarkup(keyboard)


def button_cmd(update: Update, context: CallbackContext):
    """
    foo is foo command
    """

    update.effective_message and update.effective_message.reply_text("Current number: 0",
                                                                     reply_markup=reply_markup)


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return

        # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(
        text=f"Selected option: {query.data}", reply_markup=reply_markup
    )


@hookimpl
def commands() -> hook_types.HookCommandsReturnType:

    return {
        "button": [
            button_cmd,
            CallbackQueryHandler(
                button_handler,
                # Use pattern for avoid conflicts
                pattern="^[+-0]$",
            ),
        ]
    }


@hookimpl
def commands_help(
    update: Update, context: CallbackContext
) -> hook_types.HookCommandsHelpReturnType:
    return """
    /button - example inline keyboard
    """


@hookimpl
def commands_info() -> hook_types.HookCommandsInfoReturnType:
    return [
        BotCommandInfo('/button', 'example inline keyboard',
                       scope=BotCommandScopeAllPrivateChats())
    ]
