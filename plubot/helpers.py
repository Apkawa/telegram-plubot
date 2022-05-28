from typing import Optional, Union, List, Dict

from telegram import InlineKeyboardMarkup, Message, Update, ReplyMarkup, PhotoSize, InputMedia, \
    InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio, Video
from telegram.ext import CallbackContext
from telegram.utils.helpers import DEFAULT_NONE, parse_file_input
from telegram.utils.types import ODVInput, DVInput, FileInput, JSONDict


class WithContext:
    __update: Update
    __context: CallbackContext

    def __init__(self,
                 update: Update,
                 context: CallbackContext):
        self.__update = update
        self.__context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _get_store(self) -> Dict[str, Union[Message, List[Message]]]:
        store = self.__context.chat_data.store.setdefault('message_reply', {})
        return store

    _store = property(_get_store)

    def _get_store_key(self, prefix: Optional[str] = None) -> str:
        message = self.__update.effective_message
        return f'{message.message_id}-{prefix}'

    def _get_bot_message(self, prefix: Optional[str] = None) -> Optional[
        Union[Message, List[Message]]
    ]:
        return self._store.get(self._get_store_key(prefix))

    def _set_bot_message(self,
                         message: Union[Message, List[Message]],
                         prefix: Optional[str] = None) -> None:

        self._store[self._get_store_key(prefix)] = message

    def reply_or_edit_text(self,
                           text: str,
                           parse_mode: ODVInput[str] = DEFAULT_NONE,
                           disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
                           reply_markup: InlineKeyboardMarkup = None,
                           disable_notification: DVInput[bool] = DEFAULT_NONE,
                           reply_to_message_id: int = None,
                           allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
                           protect_content: bool = None,
                           prefix: Optional[str] = None,
                           ):

        common_kw = dict(
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview
        )

        bot_message = self._get_bot_message(prefix)
        if not bot_message:
            reply_message = self.__update.message.reply_text(
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                protect_content=protect_content,
                allow_sending_without_reply=allow_sending_without_reply,
                **common_kw
            )
            self._set_bot_message(reply_message, prefix)
            return reply_message
        else:
            return self.__context.bot.edit_message_text(
                chat_id=bot_message.chat_id,
                message_id=bot_message,
                **common_kw
            )

    def reply_or_edit_photo(self,
                            photo: Union[FileInput, 'PhotoSize'],
                            caption: str = None,
                            disable_notification: DVInput[bool] = DEFAULT_NONE,
                            reply_to_message_id: int = None,
                            reply_markup: ReplyMarkup = None,
                            parse_mode: ODVInput[str] = DEFAULT_NONE,
                            allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
                            filename: str = None,
                            protect_content: bool = None,
                            prefix: Optional[str] = None,
                            ):

        common_kw = dict(
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
        bot_message = self._get_bot_message(prefix)
        if not bot_message:
            reply_message = self.__update.message.reply_photo(
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                protect_content=protect_content,
                allow_sending_without_reply=allow_sending_without_reply,
                **common_kw
            )
            self._set_bot_message(reply_message, prefix)
            return reply_message
        else:
            photo = parse_file_input(photo, PhotoSize, filename=filename)
            media = InputMediaPhoto(
                media=photo,
                caption=caption,
                parse_mode=parse_mode,
                filename=filename
            )
            return self.__context.bot.edit_message_media(
                chat_id=bot_message.chat_id,
                message_id=bot_message.message_id,
                media=media,
                reply_markup=reply_markup,
            )

    def reply_or_edit_video(self,
                            video: Union[FileInput, 'Video'],
                            duration: int = None,
                            width: int = None,
                            height: int = None,
                            supports_streaming: bool = None,
                            thumb: FileInput = None,
                            caption: str = None,
                            disable_notification: DVInput[bool] = DEFAULT_NONE,
                            reply_to_message_id: int = None,
                            reply_markup: ReplyMarkup = None,
                            parse_mode: ODVInput[str] = DEFAULT_NONE,
                            allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
                            filename: str = None,
                            protect_content: bool = None,
                            prefix: Optional[str] = None,
                            ):

        common_kw = dict(
            duration=duration,
            width=width,
            height=height,
            supports_streaming=supports_streaming,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            filename=filename,
        )
        bot_message = self._get_bot_message(prefix)
        if not bot_message:
            reply_message = self.__update.message.reply_video(
                video=video,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                protect_content=protect_content,
                allow_sending_without_reply=allow_sending_without_reply,
                **common_kw
            )
            self._set_bot_message(reply_message, prefix)
            return reply_message
        else:
            photo = parse_file_input(video, Video, filename=filename)
            media = InputMediaVideo(
                media=photo,
                **common_kw
            )
            return self.__context.bot.edit_message_media(
                chat_id=bot_message.chat_id,
                message_id=bot_message.message_id,
                media=media,
                reply_markup=reply_markup,
            )

    def reply_or_edit_media_group(
        self,
        media: List[
            Union[
                InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo
            ]
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        protect_content: bool = None,
        prefix: Optional[str] = None,
    ):

        bot_messages = self._get_bot_message(prefix)

        for m in media:
            m.caption = ''
        media[0].caption = caption
        media[0].parse_mode = parse_mode

        if not bot_messages:
            reply_message_list = self.__update.message.reply_media_group(
                media=media,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                protect_content=protect_content,
                allow_sending_without_reply=allow_sending_without_reply,
            )
        else:
            title_message = bot_messages[0]
            bot = self.__context.bot
            if title_message.caption != caption:
                bot.edit_message_caption(
                    chat_id=title_message.chat_id,
                    message_id=title_message.message_id,
                    caption=caption,
                    parse_mode=parse_mode,
                )

            if len(media) < len(bot_messages):
                to_delete_messages = bot_messages[len(media):]
                for m in to_delete_messages:
                    m.delete()
            if len(media) > len(bot_messages):
                bot.logger.warning("No append extra media into media group! Drop other media")
                media = media[:len(bot_messages)]

            reply_message_list = []
            for [_m, b_m] in zip(media, bot_messages):
                r_message = bot.edit_message_media(
                    chat_id=b_m.chat_id,
                    message_id=b_m.message_id,
                    media=_m,
                )
                reply_message_list.append(r_message)

        self._set_bot_message(reply_message_list, prefix)
        return reply_message_list
