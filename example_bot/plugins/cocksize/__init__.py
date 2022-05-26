import datetime
from random import Random

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    ParseMode,
)
from telegram.ext import CallbackContext

from plubot.plugin import hookimpl, hook_types
from plubot.utils import gen_id

EMOJI = {5: "😭", 10: "🙁", 15: "😐", 20: "😏", 25: "😮", 30: "🥳", 35: "😨", 40: "😱", 50: "😎"}


def render_cock_size_text(size: int):
    emoji = None
    for max_size, e in sorted(EMOJI.items(), key=lambda v: v[0], reverse=False):
        if max_size >= size:
            emoji = e
            break
    return f"My cock size is {size}cm {emoji}"


def get_cock_size_text(user_id):
    date = datetime.date.today().isoformat()
    seed = f"{date}-{user_id}"
    rnd = Random(seed)
    size = rnd.randint(1, 43)
    return render_cock_size_text(size)


@hookimpl
def inline_query(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:
    if not query or not update.effective_user:
        return None
    user_id = update.effective_user.id
    results = [
        InlineQueryResultArticle(
            id=gen_id(),
            title="Share your cock size",
            description="Your cock size",
            input_message_content=InputTextMessageContent(get_cock_size_text(user_id)),
            parse_mode=ParseMode.MARKDOWN_V2,
        ),
    ]
    return results
