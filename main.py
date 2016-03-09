# Shing's Telegram Scheduler Bot
# Frontend module for defining slash commands and others.
# First time trying to separate a program into a framework. Expect lots of debugging.

import telegram
import logging
from scheduler import Chat


# Universal variables (Bot setup, dictionary of chats, last chat ID)
token = '203435568:AAFtnHEPa2H1ZKLz0nX50A1K50I47sbndiA'
updater = telegram.Updater(token)
dp = updater.dispatcher
chat = {}


# Enable Logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    chat_id = update.message.chat_id
    chat[chat_id] = Chat(chat_id)
    chat[chat_id].init_complete(bot)


def new(bot, update):
    chat_id = update.message.chat_id
    chat[chat_id].newevent(bot, update)
    chat[chat_id].settitle(bot, update)
    dp.addTelegramMessageHandler(chat[chat_id].settitle2)


def schedule(bot, update):
    chat_id = update.message.chat_id
    dp.removeTelegramMessageHandler(chat[chat_id].settitle2)
    chat[chat_id].setschedule(bot, update)
    dp.addTelegramMessageHandler(chat[chat_id].setschedule2)


def done(bot, update):
    chat_id = update.message.chat_id
    dp.removeTelegramMessageHandler(chat[chat_id].setschedule2)
    chat[chat_id].setup_complete(bot, update)
    dp.addTelegramMessageHandler(chat[chat_id].display_voting)
    chat[chat_id].display_voting(bot)
    for i in range(1, len(chat[chat_id].schedule)):
        dp.addTelegramCommandHandler(str(i), chat[chat_id].selectoption)


def any_message(bot, update):
    logger.info("New message from: %s | chat_id: %d | Text: %s" %
                (update.message.from_user.username, update.message.chat_id, update.message.text))


def unknown_command(bot, update):
    # Answer in Telegram
    bot.sendMessage(update.message.chat_id, text='Command not recognized!')


def error(bot, update, error):
    # Print error to console
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    # Slash command handlers here.
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("new", new)
    dp.addTelegramCommandHandler("schedule", schedule)
    dp.addTelegramCommandHandler("done", done)

    # All other handlers here.
    dp.addUnknownTelegramCommandHandler(unknown_command)
    dp.addTelegramRegexHandler('.*', any_message)
    dp.addErrorHandler(error)

    # Start the Bot.
    updater.start_polling()


if __name__ == '__main__':
    main()
