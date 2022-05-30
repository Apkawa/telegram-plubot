# The [dict, ChatData, dict] is for type checkers like mypy
import functools
from typing import Optional, cast, Callable
from typing_extensions import TypeAlias

from telegram import Update, Message, User
from telegram.ext import CallbackContext, Dispatcher

from plubot.config import config
from plubot.plugin import hookimpl, hook_types


class ACLContext(CallbackContext):
    """Custom class for context."""
    _user_is_admin: bool

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher=dispatcher)
        self._message: Optional[Message] = None
        self._user: Optional[User] = None

    @property
    def user_is_admin(self) -> bool:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return self._user and self._user.id in config.admins

    @classmethod
    def from_update(cls, update: object, dispatcher: "Dispatcher") -> "ACLContext":
        context = cast(ACLContext, super().from_update(update, dispatcher))

        if isinstance(update, Update) and update.effective_user:
            context._user = update.effective_user
        if isinstance(update, Update) and update.effective_message:
            context._message = update.effective_message

        # Remember to return the object
        return context


TFunc: TypeAlias = Callable[[Update, ACLContext], None]


def check_permission(check_cb: Callable[[Update, ACLContext], None]) -> Callable[[TFunc], TFunc]:
    def decorator(func: TFunc) -> TFunc:
        @functools.wraps(func)
        def _wrap(update: Update, context: ACLContext) -> None:
            if check_cb(update, context):
                return func(update, context)

        return _wrap

    return decorator


allow_admin = check_permission(lambda u, cb: cb.user_is_admin)


@hookimpl
def context_class() -> hook_types.HookChatDataClassReturnType:
    return ACLContext
