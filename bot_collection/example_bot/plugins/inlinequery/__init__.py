from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    ParseMode,
    Update,
    InlineQueryResultCachedPhoto,
    InlineQueryResultPhoto,
)
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from plubot.plugin import hook_types, hookimpl
from plubot.utils import gen_id


@hookimpl
def inline_query(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:
    results = [
        InlineQueryResultArticle(
            id=gen_id(),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=gen_id(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)), parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=gen_id(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)), parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=gen_id(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)), parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]
    return results


@hookimpl(specname="inline_query")
def inline_query_other_cmd(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:
    name, extra_query = (query.split(" ", 1) + [""])[:2]
    commands = {"foo": "Foo!", "bar": "Bar!"}
    if name in commands:
        return [
            InlineQueryResultArticle(
                id=gen_id(),
                title=name,
                hide_url=True,
                description=commands[name] + extra_query,
                input_message_content=InputTextMessageContent(
                    commands[name] + extra_query
                ),
            )
        ]

    return [
        InlineQueryResultArticle(
            id=gen_id(),
            title=n,
            description=commands[n],
            input_message_content=InputTextMessageContent(commands[n]),
        )
        for n in commands
    ]


# @hookimpl(specname='inline_query', trylast=True)
def inline_query_use_api(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:

    if not update.effective_user:
        return None

    resp = context.bot.send_photo(
        update.effective_user.id,
        "https://cs14.pikabu.ru/post_img/2022/05/25/8/1653484317232388463.jpg",
    )
    context.bot.delete_message(update.effective_user.id, message_id=resp.message_id)
    return [
        InlineQueryResultCachedPhoto(
            id=gen_id(), photo_file_id=resp.photo[0].file_id, title="From cache"
        ),
        InlineQueryResultPhoto(
            id=gen_id(),
            photo_url="https://core.telegram.org/file/811140221/1/fW9vnLya4Fg/e2b5c530c7b0e019c4",
            thumb_url="https://core.telegram.org/file/811140221/1/fW9vnLya4Fg/e2b5c530c7b0e019c4",
            title="From http url",
        ),
    ]
