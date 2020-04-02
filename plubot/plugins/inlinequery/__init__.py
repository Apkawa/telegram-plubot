from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode, Update
from telegram.ext import Dispatcher, InlineQueryHandler, CallbackContext
from telegram.utils.helpers import escape_markdown

from plubot.config import hookimpl


def inlinequery(update: Update, context: CallbackContext):
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Caps",
            input_message_content=InputTextMessageContent(
                query.upper())),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
    ]

    update.inline_query.answer(results)


@hookimpl
def prepare_bot(dp: Dispatcher):
    dp.add_handler(InlineQueryHandler(inlinequery))
