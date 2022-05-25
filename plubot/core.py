import logging
import string
from importlib import import_module

from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, InlineQueryHandler, Dispatcher, CommandHandler
from telegram.utils.helpers import escape_markdown

from plubot.config import config
# Enable logging
from plubot.plugin.manager import get_plugin_manager
from plubot.utils import import_from_path

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

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
        self._load_plugins()

    def _load_plugins(self):
        for p in config.plugins:
            self._load_plugin(p)

    def _load_plugin(self, plugin_name: str):
        if '.' not in plugin_name:
            # maybe relative
            plugin_name = config.module.__name__ + '.plugins.' + plugin_name
        p_m = import_module(plugin_name)
        self.plugin_manager.register(p_m)

    def _inline_query(self, update: Update, context: CallbackContext):
        query = update.inline_query.query.strip()

        hook_results = self.hook.inline_query(query=query, update=update, context=context)

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
            for name, cb in c.items():
                if name not in flatten_commands:
                    flatten_commands[name] = cb
                else:
                    raise ValueError(f'{name} already exists!')

        def start_handler(update: Update, context: CallbackContext):
            update.message.reply_text("Hi! Use /help command for instructions")

        def help_handler(update: Update, context: CallbackContext):
            help_text = '\n'.join(['\n'.join(map(str.strip, h.splitlines())) for h in
                                   self.hook.help(update=update, context=context) if h])

            update.message.reply_text(
                escape_markdown(help_text, version=2),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
            )

        dp.add_handler(CommandHandler('start', start_handler))
        dp.add_handler(CommandHandler('help', help_handler))

        for name, cb in flatten_commands.items():
            if isinstance(cb, CommandHandler):
                dp.add_handler(cb)
            else:
                dp.add_handler(CommandHandler(name, cb, pass_args=True, allow_edited=False))

    def init(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater(
            self.token,
            use_context=True,
            request_kwargs={'proxy_url': config.proxy}
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
