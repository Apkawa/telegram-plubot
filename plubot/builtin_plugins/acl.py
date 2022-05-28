# The [dict, ChatData, dict] is for type checkers like mypy
import functools
import typing

from telegram import Update, Message, User
from telegram.ext import CallbackContext, Dispatcher

from plubot.config import config
from plubot.plugin import hookimpl, hook_types


class ACLContext(CallbackContext):
    """Custom class for context."""
    _user_is_admin: bool

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher=dispatcher)
        self._message: typing.Optional[Message] = None
        self._user: typing.Optional[User] = None

    @property
    def user_is_admin(self) -> bool:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return self._user and self._user.id in config.admins

    @classmethod
    def from_update(cls, update: object, dispatcher: "Dispatcher") -> "ACLContext":
        context = typing.cast(ACLContext, super().from_update(update, dispatcher))

        if isinstance(update, Update) and update.effective_user:
            context._user = update.effective_user
        if isinstance(update, Update) and update.effective_message:
            context._message = update.effective_message

        # Remember to return the object
        return context


def allow_admin(func):
    @functools.wraps(func)
    def _wrap(update: Update, context: ACLContext) -> None:
        if context.user_is_admin:
            func(update, context)

    return _wrap


@hookimpl
def context_class() -> hook_types.HookChatDataClassReturnType:
    return ACLContext
