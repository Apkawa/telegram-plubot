import base64
import string
from typing import Tuple, Callable, List
from uuid import uuid4

from PIL import Image
from meme_generator.memes.supermind import SupermindMeme
from telegram import InlineQueryResult, InputTextMessageContent, InlineQueryResultArticle, \
    ParseMode, InlineQueryResultPhoto, Update, InlineQueryResultCachedPhoto
from telegram.ext import Dispatcher, Updater, CallbackContext
from telegram.utils.helpers import escape_markdown

from plubot.config import hookimpl


def meme_handler(query, update: Update, context: CallbackContext):
    """
    too | bar |nya | up to 10
    :param query:
    :return:
    """
    minds = list(map(str.strip, query.split("|")))
    if not minds:
        return
    r = SupermindMeme()
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
