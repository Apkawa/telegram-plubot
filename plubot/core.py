import logging
import sys
import types
from importlib import import_module
from pathlib import Path
from typing import Union, Optional

from telegram import (
    Update, ParseMode,
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllChatAdministrators,
)
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

from plubot import builtin_plugins
from plubot.bot_command import group_bot_command_info, BotCommandInfo
from plubot.config import config

# Enable logging
from plubot.plugin.manager import get_plugin_manager
from plubot.utils import import_from_path, remove_jobs

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

bot_logger = logging.getLogger("telegram.bot")
bot_logger.setLevel(logging.DEBUG)
bot_logger.addHandler(logging.StreamHandler())

logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.exception('Update "%s" caused error "%s"', update, context.error)


class PluBot:
    def __init__(self, path: str):
        self.plugin_manager = get_plugin_manager()
        self._load(path)
        self.hook = self.plugin_manager.hook
        self.token = config.token

    def _load(self, path: str):
        sys.path.append(str(Path(path).absolute().parent))
        module = import_from_path(path)
        config.load(module)
        self._load_plugins(config.plugins)
        self._load_plugin(builtin_plugins)

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
        name = f'__inline_query_{update.effective_user.id}'
        remove_jobs(name, context)
        _update = update
        _context = context

        def _query_cb(context: CallbackContext):
            remove_jobs(name, context)
            query = _update.inline_query.query.strip()

            hook_results = self.hook.inline_query(
                query=query, update=_update, context=_context
            )

            results = []
            for r in hook_results:
                if not r:
                    continue
                if isinstance(r, list):
                    results.extend(r)

            if results:
                _update.inline_query.answer(
                    results,
                    cache_time=0,
                )

        # keyboard typing filter
        context.job_queue.run_once(_query_cb, when=1.0, name=name)

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
                    "\n".join(filter(None, map(str.strip, h.strip().splitlines())))
                    for h in self.hook.commands_help(update=update, context=context)
                    if h
                ]
            )
            if update.message and help_text:
                update.message.reply_text(
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
                        CommandHandler(name, c, pass_args=True, allow_edited=True)
                    )

    def _init_commands_button(self, dp: Dispatcher):
        """
        https://core.telegram.org/bots/api#determining-list-of-commands
        """
        # Cleanup old commands
        default_scopes = [
            BotCommandScopeDefault(),
            BotCommandScopeAllPrivateChats(),
            BotCommandScopeAllGroupChats(),
            BotCommandScopeAllChatAdministrators(),
        ]
        for scope in default_scopes:
            for lang in [None, 'ru', 'en']:
                dp.bot.delete_my_commands(scope=scope, language_code=lang)
        commands_info = [[
            BotCommandInfo('help', 'Help', scope=default_scopes),
            BotCommandInfo('help', '??????????????', language_code='ru', scope=default_scopes)
        ]]
        extra_commands_info = self.hook.commands_info()
        if extra_commands_info:
            commands_info.extend(extra_commands_info)
        groups_commands = group_bot_command_info(commands_info)
        for g in groups_commands:
            dp.bot.set_my_commands(**g)

    def _build_context_types(self) -> ContextTypes:
        kw = {}

        for k in ['bot_data', 'chat_data', 'user_data', 'context']:
            class_list = getattr(self.hook, f'{k}_class')()
            if class_list:
                # TODO test shadow
                cls = type(f"Custom{k.title().replace('_', '')}", tuple(class_list), {})
                kw[k] = cls

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
        self._init_commands_button(dp)
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
