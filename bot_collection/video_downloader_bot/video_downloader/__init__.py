import os.path
from hashlib import sha1

from telegram import (
    Update, ChatAction, Video,
    InlineQueryResultCachedVideo,
    Animation
)
from telegram.ext import CallbackContext, MessageHandler, Filters

from plubot.plugin import hookimpl, hook_types
from plubot.utils import gen_id

from .converter import Converter
from .utils import extract_links
from .video import extract_video, VideoLinkResult, process_link, ProcessState


def handle_links(update: Update, context: CallbackContext) -> None:
    message = update.message
    context.bot.send_chat_action(
        chat_id=message.chat_id,
        action=ChatAction.TYPING
    )
    raw_links = extract_links(update.message.text)

    cache = context.chat_data.store.sub_store("video_cache")

    message = update.effective_message
    for i, raw_link in enumerate(raw_links):
        video_list_process = process_link(raw_link, cache)
        for gen_process in video_list_process:
            context.bot.send_chat_action(
                chat_id=message.chat_id,
                action=ChatAction.UPLOAD_VIDEO
            )
            bot_message = message.reply_text("Downloading video...", disable_notification=True)
            for process_result in gen_process:
                if process_result.state == ProcessState.CONVERT:
                    bot_message.edit_text("Converting video...")
                if process_result.state == ProcessState.ERROR:
                    context.bot.logger.exception(f"Process video error: {process_result.error}")
                    bot_message.edit_text(f"Process video error: {process_result.error}")
                elif process_result.state == ProcessState.READY:
                    bot_message.edit_text("Uploading video...")
                    v_result = process_result.result
                    try:
                        reply = update.message.reply_video(
                            v_result.video,
                            filename="@yet_video_downloader" + v_result.name,
                            reply_to_message_id=update.message.message_id
                        )
                        gen_process.send(reply.effective_attachment)
                        bot_message.delete()
                    except Exception as e:
                        context.bot.logger.exception(f"Process video error: {e}")
                        bot_message.edit_text(f"Process video error: {e}")
                        continue


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

    links, *caption_parts = query.split("|")
    raw_links = extract_links(links)

    cache = context.bot_data.store.sub_store("video_cache")

    results = []

    for i, raw_link in enumerate(raw_links):
        video_list_process = process_link(raw_link, cache)
        for gen_process in video_list_process:
            for process_result in gen_process:
                if process_result.state != ProcessState.READY:
                    continue
                v_result = process_result.result
                video = v_result.video
                if not isinstance(video, Video):
                    resp = context.bot.send_video(
                        video=video,
                        filename="@yet_video_downloader" + v_result.name,
                        chat_id=update.effective_user.id,
                        disable_notification=True,
                    )
                    video = resp.effective_attachment
                    resp.delete()

                title = "Video"
                if caption_parts:
                    title = " ".join(caption_parts)
                i_q = InlineQueryResultCachedVideo(
                    id=gen_id(),
                    video_file_id=video.file_id,
                    title=title,
                    caption=" ".join(caption_parts),

                )
                gen_process.send(video)
                results.append(i_q)
    return results
