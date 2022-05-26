import logging
import types
from importlib import import_module
from typing import Union

from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CallbackContext,
    InlineQueryHandler,
    Dispatcher,
    CommandHandler,
    Handler,
    ContextTypes,
)
from telegram.utils.helpers import escape_markdown

from plubot.config import config

# Enable logging
from plubot.plugin.manager import get_plugin_manager
from plubot.utils import import_from_path

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

bot_logger = logging.getLogger("telegram.bot")
bot_logger.setLevel(logging.DEBUG)
bot_logger.addHandler(logging.StreamHandler())

logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


class PluBot:
    def __init__(self, path: str):
        self.plugin_manager = get_plugin_manager()
        self._load(path)
        self.hook = self.plugin_manager.hook
        self.token = config.token

    def _load(self, path: str):
        module = import_from_path(path)
        config.load(module)
        self._load_plugins(config.plugins)

    def _load_plugins(self, plugins):
        for p in plugins:
            self._load_plugin(p)

    def _load_plugin(self, plugin_name: Union[str, object, types.ModuleType]):
        p_m: Union[object, types.ModuleType]
        if isinstance(plugin_name, str):
            if "." not in plugin_name:
                # maybe relative
                plugin_name = config.module.__name__ + ".plugins." + plugin_name
            p_m = import_module(plugin_name)
        else:
            p_m = plugin_name
        self.plugin_manager.register(p_m)
        extra_plugins = getattr(p_m, "PLUGINS", [])
        self._load_plugins(extra_plugins)

    def _inline_query(self, update: Update, context: CallbackContext):
        if not update.inline_query:
            return
        query = update.inline_query.query.strip()

        hook_results = self.hook.inline_query(
            query=query, update=update, context=context
        )

        results = []
        for r in hook_results:
            if not r:
                continue
            if isinstance(r, list):
                results.extend(r)

        if results:
            update.inline_query.answer(results)

    def _init_commands(self, dp: Dispatcher):
        commands = self.hook.commands()
        flatten_commands = {}
        for c in commands:
            for name, cb_list in c.items():
                if name not in flatten_commands:
                    flatten_commands[name] = cb_list
                else:
                    raise ValueError(f"{name} already exists!")

        def start_handler(update: Update, context: CallbackContext):
            update.message and update.message.reply_text(
                "Hi! Use /help command for instructions"
            )

        def help_handler(update: Update, context: CallbackContext):
            help_text = "\n".join(
                [
                    "\n".join(map(str.strip, h.strip().splitlines()))
                    for h in self.hook.commands_help(update=update, context=context)
                    if h
                ]
            )

            update.message and update.message.reply_text(
                escape_markdown(help_text, version=2),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
            )

        dp.add_handler(CommandHandler("start", start_handler, allow_edited=False))
        dp.add_handler(CommandHandler("help", help_handler, allow_edited=False))

        for name, cb_list in flatten_commands.items():
            if not isinstance(cb_list, (list, tuple)):
                cb_list = [cb_list]
            for c in cb_list:
                if isinstance(c, Handler):
                    dp.add_handler(c)
                else:
                    dp.add_handler(
                        CommandHandler(name, c, pass_args=True, allow_edited=False)
                    )

    def _build_context_types(self) -> ContextTypes:
        kw = {}

        chat_data_class_list = self.hook.chat_data_class()
        if chat_data_class_list:
            # TODO test shadow
            chat_data_cls = type("CustomChatData", tuple(chat_data_class_list), {})
            kw["chat_data"] = chat_data_cls

        context_class_list = self.hook.context_class()
        if context_class_list:
            # TODO test shadow
            context_cls = type("CustomContext", tuple(context_class_list), {})
            kw["context"] = context_cls

        return ContextTypes(**kw)

    def init(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater(
            self.token,
            use_context=True,
            context_types=self._build_context_types(),
            request_kwargs={"proxy_url": config.proxy},
        )

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(InlineQueryHandler(self._inline_query))
        self._init_commands(dp)
        self.hook.prepare_bot(dp=dp)

        # log all errors
        dp.add_error_handler(error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


def main(path: str):
    p = PluBot(path=path)
    p.init()
