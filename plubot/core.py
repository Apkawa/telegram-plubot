import logging
from uuid import uuid4

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CallbackContext, InlineQueryHandler

from plubot import config
# Enable logging
from plubot.plugin_manager import get_plugin_manager

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
    def __init__(self, token: str):
        plugin_manager = get_plugin_manager()
        self.hook = plugin_manager.hook
        self.token = token

    def _inline_query(self, update: Update, context: CallbackContext):
        cmd_map = {k: cb for k, cb in
                   sorted(self.hook.inline_query_cmd_info(),
                          key=lambda x: x[0])}

        query = update.inline_query.query.strip()
        cmd, sub_query = (query.split(' ', 1) + ['', ''])[:2]

        if cmd in cmd_map:
            results = cmd_map[cmd](sub_query, update, context)
        else:
            results = [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=c,
                    description=cb.__doc__,
                    input_message_content=InputTextMessageContent(c),
                )
                for c, cb in cmd_map.items()]

        if results:
            update.inline_query.answer(results)

    def init(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater(
            self.token,
            use_context=True,
            request_kwargs=config.REQUEST_KWARGS
        )

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(InlineQueryHandler(self._inline_query))
        self.hook.prepare_bot(dp=dp)

        # log all errors
        dp.add_error_handler(error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


def main():
    p = PluBot(token=config.TOKEN)
    p.init()
