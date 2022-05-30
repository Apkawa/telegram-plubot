import functools
from typing import cast
from uuid import uuid4

from telegram import (
    Update,
    InlineQueryResultCachedPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent)
from telegram.ext import CallbackContext, CommandHandler

from plubot.helpers import WithContext
from plubot.plugin import hookimpl, hook_types

from meme_generator.memes.borgar import BorgarMeme
from meme_generator.memes.pooh import PoohMeme
from meme_generator.memes.supermind import SupermindMeme

from plubot.utils import gen_id

MEME_MAP = {
    'pooh': PoohMeme,
    'supermind': SupermindMeme,
    'borgar': BorgarMeme,
}


def meme_handler(update: Update, context: CallbackContext, meme_name: str):
    query = " ".join(context.args)
    minds = list(map(str.strip, query.split("|")))
    if not query or not minds:
        # TODO help text
        return

    r = MEME_MAP[meme_name]()
    fp = r.render(minds)

    with WithContext(update, context) as c:
        c.reply_or_edit_photo(
            photo=fp,
            disable_notification=True,
        )


@hookimpl
def commands() -> hook_types.HookCommandsReturnType:
    return {
        meme_name: CommandHandler(
            command=meme_name,
            callback=cast(hook_types.GenericHandlerCallback,
                          functools.partial(meme_handler, meme_name=meme_name)),
            allow_edited=True
        )
        for meme_name in MEME_MAP
    }


@hookimpl
def inline_query(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:
    meme_name, query = (query.split(' ', 1) + [''])[:2]
    if meme_name not in MEME_MAP:
        results = [
            InlineQueryResultArticle(
                id=gen_id(),
                title=c,
                description=cb.__doc__,
                input_message_content=InputTextMessageContent(c),
            )
            for c, cb in MEME_MAP.items()
        ]
        return results

    minds = list(map(str.strip, query.split("|")))
    if not minds:
        return

    r = MEME_MAP[meme_name]()
    fp = r.render(minds)

    resp = context.bot.send_photo(
        chat_id=update.effective_user.id,
        photo=fp,
        disable_notification=True,
    )
    context.bot.delete_message(
        update.effective_user.id,
        message_id=resp.message_id)
    return [
        InlineQueryResultCachedPhoto(
            id=gen_id(),
            photo_file_id=resp.photo[0].file_id,
            title=meme_name
        )
    ]


@hookimpl
def commands_info() -> hook_types.HookCommandsInfoReturnType:
    return [
        [meme, f'Make "{meme}" meme']
        for meme in MEME_MAP
    ]


@hookimpl
def commands_help(
    update: Update, context: CallbackContext
) -> hook_types.HookCommandsHelpReturnType:
    return "\n".join([f'/{m} - {c}' for m, c in commands_info()])
