import os

from telegram import Update, BotCommandScopeAllPrivateChats, BotCommandScopeAllChatAdministrators, \
    InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from plubot.bot_command import BotCommandInfo
from plubot.helpers import WithContext
from plubot.plugin import hook_types, hookimpl

from . import simple_inlinekeyboard, context_types, reply_keyboard

# Plugins decomposition
PLUGINS = [simple_inlinekeyboard, context_types, reply_keyboard]


# More examples
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v13.11/examples


@hookimpl
def prepare_bot(dp: Dispatcher) -> None:
    pass


def _get_reply_markup(args):
    _keyboard = [
        InlineKeyboardButton(a, callback_data="xxx")
        for a in args
    ]
    _reply_markup = None
    if _keyboard:
        _reply_markup = InlineKeyboardMarkup([_keyboard])
    return _reply_markup


def foo_cmd(update: Update, context: CallbackContext):
    """
    foo is foo command
    """
    text = f"Foo command execute with args {context.args}"

    with WithContext(update, context) as c:
        if (
            context.args
            and context.args[0].startswith('https://')
            and os.path.splitext(context.args[0])[-1].lower() in ['.png', '.jpeg', '.jpg']
        ):
            reply_markup = _get_reply_markup(context.args[1:])
            c.reply_or_edit_photo(
                photo=context.args[0],
                caption=text,
                reply_to_message_id=update.effective_message.message_id,
                reply_markup=reply_markup
            )
        else:
            reply_markup = _get_reply_markup(context.args)
            c.reply_or_edit_text(text,
                                 reply_to_message_id=update.effective_message.message_id,
                                 disable_web_page_preview=True,
                                 reply_markup=reply_markup)


# Use chat data instead
MESSAGE_REPLY = {}

keyboard = [
    [
        InlineKeyboardButton("❤", callback_data="like"),
        InlineKeyboardButton("💋", callback_data="chmoo"),
    ],
    [InlineKeyboardButton("🍆", callback_data="benis")],
]
reply_markup = InlineKeyboardMarkup(keyboard)


def bar_cmd(update: Update, context: CallbackContext):
    """
    bar is bar command
    """
    with WithContext(update, context) as c:
        c.reply_or_edit_text(f'Bar with context args: {context.args}',
                             reply_to_message_id=update.effective_message.message_id,
                             disable_web_page_preview=True)
        if (
            context.args
            and context.args[0].startswith('https://')
            and os.path.splitext(context.args[0])[-1].lower() in ['.png', '.jpeg', '.jpg']
        ):
            if len(context.args) == 1:
                c.reply_or_edit_photo(
                    context.args[0],
                    caption=f'photo  {os.path.split(context.args[0])[-1]}',
                    prefix="1",
                    reply_markup=reply_markup,
                )
            else:
                media = [InputMediaPhoto(media=a) for a in context.args]
                c.reply_or_edit_media_group(
                    media,
                    caption=str([
                        os.path.split(a)[-1]
                        for a in context.args
                    ]),
                    prefix="mg",

                )
        else:
            c.reply_or_edit_text(f'1 {context.args}', prefix="1")


def video_cmd(update: Update, context: CallbackContext):
    text = f"with args {context.args}"

    with WithContext(update, context) as c:
        reply_markup = _get_reply_markup(context.args[2:])
        c.reply_or_edit_video(
            video=context.args[0],
            caption=text,
            reply_to_message_id=update.effective_message.message_id,
            reply_markup=reply_markup
        )


@hookimpl
def commands() -> hook_types.HookCommandsReturnType:
    return {
        "foo": foo_cmd,
        "bar": CommandHandler("bar", bar_cmd, pass_args=True),
        "video": video_cmd,
    }


@hookimpl
def commands_info() -> hook_types.HookCommandsInfoReturnType:
    return [
        ('foo', 'Foo command'),
        BotCommandInfo('foo', 'Команда Фу!', language_code='ru'),
        BotCommandInfo('bar', 'Го в бар', language_code='ru',
                       scope=[
                           BotCommandScopeAllPrivateChats(),
                           BotCommandScopeAllChatAdministrators()
                       ]),
        BotCommandInfo('bar', 'Go fucking bar!', language_code=None,
                       scope=[
                           BotCommandScopeAllPrivateChats(),
                           BotCommandScopeAllChatAdministrators()
                       ]
                       ),
    ]


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
