import datetime
from random import Random
from math import floor, ceil

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    ParseMode,
)
from telegram.ext import CallbackContext

from plubot.config import config
from plubot.plugin import hookimpl, hook_types
from plubot.utils import gen_id

EMOJI = {5: "😭", 10: "🙁", 15: "😐", 20: "😏", 25: "😮", 30: "🥳", 35: "😨", 40: "😱", 50: "😎"}


def get_emoji(i: int, min_size: int = 1, max_size: int = 50):
    """
    >>> get_emoji(1, min_size=0, max_size=10)
    '😭'
    >>> get_emoji(2, min_size=0, max_size=10)
    '🙁'
    >>> get_emoji(3, min_size=0, max_size=10)
    '😐'
    >>> get_emoji(4, max_size=50)
    '😭'
    >>> get_emoji(9, max_size=50)
    '🙁'
    >>> get_emoji(11, max_size=50)
    '😐'
    >>> get_emoji(17, max_size=50)
    '😏'
    >>> get_emoji(45, max_size=50)
    '😎'
    >>> get_emoji(55, max_size=50)
    '😎'
    """
    if i > max_size:
        i = max_size
    step = (max_size - min_size) / len(EMOJI)
    e_list = list(EMOJI.values())
    e_i = floor(i / step)
    if e_i >= len(e_list):
        e_i = len(e_list) - 1
    return e_list[e_i]


def render_cock_size_text(size: int):
    emoji = None
    for max_size, e in sorted(EMOJI.items(), key=lambda v: v[0], reverse=False):
        if max_size >= size:
            emoji = e
            break
    return f"My cock size is {size}cm {emoji}"


def get_cock_size_gaussan(seed: str, min_size=1, max_size=50):
    rnd = Random(seed)
    size = int(rnd.gauss(mu=(max_size / 2) - 5, sigma=max_size / 6))
    if size < min_size:
        size = min_size
    elif size > max_size:
        size = max_size
    return size


def get_cock_size_randint(seed: str, min_size=1, max_size=50):
    rnd = Random(seed)

    size = rnd.randint(min_size, max_size)
    return size


get_cock_size = get_cock_size_gaussan


def build_seed(user_id):
    date = datetime.date.today().isoformat()
    secret = config.seed_secret
    seed = f"{secret}-{date}-{user_id}"
    return seed


def get_cock_size_text(user_id,
                       template="My cock size is {size}cm {emoji}",
                       min_size=1,
                       max_size=50):
    seed = build_seed(user_id)
    size = get_cock_size(seed, min_size=min_size, max_size=max_size)
    emoji = get_emoji(size, min_size=min_size, max_size=max_size)
    return template.format(emoji=emoji, size=size)


@hookimpl
def inline_query(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:
    if not update.effective_user:
        return None
    user_id = update.effective_user.id
    cock_size = get_cock_size_text(user_id)
    clitoris_size = get_cock_size_text(user_id,
                                  template='My clitoris size is {size}mm {emoji}',
                                  min_size=4,
                                  max_size=100,
                                  )
    results = [
        InlineQueryResultArticle(
            id=gen_id(),
            title="Share your cock size",
            description="Your cock size",
            input_message_content=InputTextMessageContent(cock_size),
            parse_mode=ParseMode.MARKDOWN_V2,
        ),
        InlineQueryResultArticle(
            id=gen_id(),
            title="Share your clitoris size",
            description="Your clitoris size",
            input_message_content=InputTextMessageContent(clitoris_size),
            parse_mode=ParseMode.MARKDOWN_V2,
        ),
    ]
    return results
