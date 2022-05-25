from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode, Update, \
    InlineQueryResultCachedPhoto, InlineQueryResultPhoto
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from plubot.plugin import hook_types, hookimpl


@hookimpl
def inline_query(query: str, update: Update,
                 context: CallbackContext) -> hook_types.HookInlineQueryReturnType:
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
    return results


@hookimpl(specname='inline_query')
def inline_query_other_cmd(query: str, update: Update,
                           context: CallbackContext) -> hook_types.HookInlineQueryReturnType:
    name, extra_query = (query.split(' ', 1) + [''])[:2]
    commands = {
        'foo': 'Foo!',
        'bar': 'Bar!'
    }
    if name in commands:
        return [
            InlineQueryResultArticle(
                id=uuid4(),
                title=name,
                hide_url=True,
                description=commands[name],
                input_message_content=InputTextMessageContent(commands[name] + extra_query),
            )
        ]

    return [
        InlineQueryResultArticle(
            id=uuid4(),
            title=n,
            description=commands[n],
            input_message_content=InputTextMessageContent(commands[n]),
        )
        for n in commands
    ]


@hookimpl(specname='inline_query', trylast=True)
def inline_query_use_api(query: str, update: Update,
                         context: CallbackContext) -> hook_types.HookInlineQueryReturnType:
    resp = context.bot.send_photo(
        update.effective_user.id,
        'https://cs14.pikabu.ru/post_img/2022/05/25/8/1653484317232388463.jpg')
    context.bot.delete_message(
        update.effective_user.id,
        message_id=resp.message_id)
    return [
        InlineQueryResultCachedPhoto(
            id=uuid4(),
            photo_file_id=resp.photo[0].file_id,
            title="From cache"
        ),
    InlineQueryResultPhoto(
            id=uuid4(),
            photo_url='https://core.telegram.org/file/811140221/1/fW9vnLya4Fg/e2b5c530c7b0e019c4',
            thumb_url='https://core.telegram.org/file/811140221/1/fW9vnLya4Fg/e2b5c530c7b0e019c4',
            title="From http url"
        )
    ]
