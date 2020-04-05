from typing import Tuple, Callable, List
from typing import Tuple, Callable, List
from uuid import uuid4

from meme_generator.memes.pooh import PoohMeme
from meme_generator.memes.supermind import SupermindMeme
from meme_generator.memes.borgar import BorgarMeme

from telegram import (
    InlineQueryResult, Update,
    InlineQueryResultCachedPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent)
from telegram.ext import CallbackContext

from plubot.config import hookimpl

MEME_MAP = {
    'pooh': PoohMeme,
    'supermind': SupermindMeme,
    'borgar': BorgarMeme,
}


def meme_handler(query, update: Update, context: CallbackContext):
    """
    too | bar |nya | up to 10
    :param query:
    :return:
    """
    if not query:
        return
    meme_name, query = (query.split(' ', 1) + [''])[:2]
    minds = list(map(str.strip, query.split("|")))
    if not minds:
        return
    if meme_name not in MEME_MAP:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=c,
                description=cb.__doc__,
                input_message_content=InputTextMessageContent(c),
            )
            for c, cb in MEME_MAP.items()]
        return results

    r = MEME_MAP[meme_name]()
    fp = r.render(minds)

    resp = context.bot.send_photo(update.effective_user.id, fp)
    context.bot.delete_message(
        update.effective_user.id,
        message_id=resp.message_id)
    return [
        InlineQueryResultCachedPhoto(
            id=uuid4(),
            photo_file_id=resp.photo[0].file_id,
            title="Caps"
        )
    ]


@hookimpl
def inline_query_cmd_info() -> Tuple[str, Callable[[str], List[InlineQueryResult]]]:
    '''
    Example command
    '''
    return ['meme', meme_handler]
