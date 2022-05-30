"""
Simple Bot to showcase `telegram.ext.ContextTypes`.
Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
From
https://github.com/python-telegram-bot/python-telegram-bot/blob/v13.11/examples/contexttypesbot.py
"""
import typing
from collections import defaultdict
from typing import DefaultDict, Optional, Set

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    TypeHandler,
    Dispatcher,
)

from plubot.plugin import hookimpl, hook_types


class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    # May use external store

    def __init__(self) -> None:
        super().__init__()
        self.clicks_per_message: DefaultDict[int, int] = defaultdict(int)


# The [dict, ChatData, dict] is for type checkers like mypy
class CustomContext(CallbackContext[dict, ChatData, dict]):
    """Custom class for context."""
    chat_data: ChatData

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher=dispatcher)
        self._message_id: Optional[int] = None

    @property
    def bot_user_ids(self) -> Set[int]:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return typing.cast(Set[int], self.bot_data.setdefault("user_ids", set()))

    @property
    def message_clicks(self) -> int:
        """Access the number of clicks for the message this context object was built for."""
        if self._message_id:
            return self.chat_data.clicks_per_message[self._message_id]
        return 0

    @message_clicks.setter
    def message_clicks(self, value: int) -> None:
        """Allow to change the count"""
        if not self._message_id:
            raise RuntimeError(
                "There is no message associated with this context obejct."
            )
        self.chat_data.clicks_per_message[self._message_id] = value

    @classmethod
    def from_update(cls, update: object, dispatcher: "Dispatcher") -> "CustomContext":
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = typing.cast(CustomContext, super().from_update(update, dispatcher))

        if (
            context.chat_data
            and isinstance(update, Update)
            and update.effective_message
        ):
            context._message_id = (
                update.effective_message.message_id
            )  # pylint: disable=W0212

        # Remember to return the object
        return context


def start(update: Update, context: CustomContext) -> None:
    """Display a message with a button."""
    update.message and update.message.reply_html(
        "This button was clicked <i>0</i> times.",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Click me!", callback_data="button")
        ),
    )


def count_click(update: Update, context: CustomContext) -> None:
    """Update the click count for the message."""
    context.message_clicks += 1
    if not update.callback_query or not update.effective_message:
        return
    update.callback_query.answer()
    update.effective_message.edit_text(
        f"This button was clicked <i>{context.message_clicks}</i> times.",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Click me!", callback_data="button")
        ),
        parse_mode=ParseMode.HTML,
    )


def print_users(update: Update, context: CustomContext) -> None:
    """Show which users have been using this bot."""
    update.message and update.message.reply_text(
        "The following user IDs have used this bot: "
        f'{", ".join(map(str, context.bot_user_ids))}'
    )


def track_users(update: Update, context: CustomContext) -> None:
    """Store the user id of the incoming update, if any."""
    if update.effective_user:
        context.bot_user_ids.add(update.effective_user.id)


@hookimpl
def chat_data_class() -> hook_types.HookChatDataClassReturnType:
    return ChatData


@hookimpl
def context_class() -> hook_types.HookChatDataClassReturnType:
    return CustomContext


@hookimpl
def prepare_bot(dp: Dispatcher) -> None:
    dispatcher = dp
    dispatcher.add_handler(TypeHandler(Update, track_users), group=-1)
    dispatcher.add_handler(CommandHandler("ct", start))
    dispatcher.add_handler(CallbackQueryHandler(count_click, pattern="^button$"))
    dispatcher.add_handler(CommandHandler("print_users", print_users))
