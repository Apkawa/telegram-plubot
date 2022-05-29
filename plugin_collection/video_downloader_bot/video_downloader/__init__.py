import os.path
from hashlib import sha1

from telegram import (
    Update, ChatAction, Video,
    InlineQueryResultCachedVideo,
    InlineQueryResultVideo, Animation
)
from telegram.ext import CallbackContext, MessageHandler, Filters

from plubot.helpers import WithContext
from plubot.plugin import hookimpl, hook_types
from plubot.utils import gen_id
from .converter import Converter
from .utils import extract_links
from .video import extract_video_from_links


def handle_links(update: Update, context: CallbackContext) -> None:
    message = update.message
    context.bot.send_chat_action(
        chat_id=message.chat_id,
        action=ChatAction.TYPING
    )
    raw_links = extract_links(update.message.text)
    video_links = extract_video_from_links(raw_links)

    cache = context.chat_data.store.sub_store("video_cache")
    conv = Converter(workdir='/tmp/')
    filepath = None

    message = update.effective_message
    for i, link in enumerate(video_links):
        if not link:
            continue
        context.bot.send_chat_action(
            chat_id=message.chat_id,
            action=ChatAction.UPLOAD_VIDEO
        )
        bot_message = message.reply_text("Downloading video...", disable_notification=True)
        link_hash = None
        if isinstance(link, str):
            # Other links must be already converted
            link_hash = sha1(link.encode("utf-8")).hexdigest()
            cached_link = cache.get(link_hash)
            if cached_link:
                link = Video(**cached_link)
            else:
                ext = os.path.splitext(link)[-1]

                if ext in ['.webm']:
                    bot_message.edit_text("Converting video...")
                    filepath = conv.fetch(link)
                    link = open(conv.to_mp4(filepath), 'rb')

        bot_message.edit_text("Uploading video...")

        reply = update.message.reply_video(
            link,
            reply_to_message_id=update.message.message_id
        )

        bot_message.delete()

        if link_hash:
            cache[link_hash] = (reply.video or reply.animation).to_dict()
        if filepath:
            conv.delete(filepath)
            conv.delete(link)


@hookimpl
def commands() -> hook_types.HookCommandsReturnType:
    return {
        'handle_links': MessageHandler(callback=handle_links,
                                       filters=Filters.text & ~Filters.command,
                                       edited_updates=False
                                       )
    }


@hookimpl
def inline_query(
    query: str, update: Update, context: CallbackContext
) -> hook_types.HookInlineQueryReturnType:

    raw_links = extract_links(query)
    video_links = extract_video_from_links(raw_links)

    cache = context.bot_data.store.sub_store("video_cache")

    conv = Converter(
        workdir='/tmp/'
    )
    results = []

    for i, link in enumerate(video_links):
        filepath = conv_filepath = cached_link = link_hash = None
        if not link:
            continue
        if isinstance(link, str):
            # Other links must be already converted
            link_hash = sha1(link.encode("utf-8")).hexdigest()
            cached_link = cache.get(link_hash)
            if cached_link:
                link = Video(**cached_link)
            else:
                ext = os.path.splitext(link)[-1]

                if ext in ['.webm']:
                    filepath = conv.fetch(link)
                    link = conv_filepath = conv.to_mp4(filepath)
                    resp = context.bot.send_video(
                        chat_id=update.effective_user.id,
                        video=open(link, 'rb'),
                        disable_notification=True,
                    )
                    link = resp.video
                    resp.delete()

        if not cached_link:
            resp = context.bot.send_video(
                chat_id=update.effective_user.id,
                video=link,
                disable_notification=True,
            )
            link = resp.video or resp.animation
            if link_hash and isinstance(link, (Video, Animation)):
                cache[link_hash] = link.to_dict()
            resp.delete()

        if filepath:
            conv.delete(filepath)
            conv.delete(conv_filepath)

        i_q = InlineQueryResultCachedVideo(
            id=gen_id(),
            video_file_id=link.file_id,
            title='Video',
        )
        results.append(i_q)

    return results
