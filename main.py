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
    try:
        chat[chat_id]
    except KeyError:
        chat[chat_id] = Chat(chat_id)
        chat[chat_id].init_complete(bot)
    else:
        try:
            chat[chat_id.schedule]
        except AttributeError:
            pass
        else:
            for x in range(1, len(chat[chat_id].schedule)+1):
                dp.removeTelegramCommandHandler(str(x), chat[chat_id].selectoption)
        dp.removeTelegramMessageHandler(chat[chat_id].set_date)
        dp.removeTelegramMessageHandler(chat[chat_id].set_date2)
        dp.removeTelegramMessageHandler(chat[chat_id].newevent2)
        dp.removeTelegramMessageHandler(chat[chat_id].settitle2)
        dp.removeTelegramMessageHandler(chat[chat_id].setschedule2)
        dp.removeTelegramMessageHandler(chat[chat_id].display_voting)
        chat[chat_id].init_restart(bot)


def newevent(bot, update):
    chat_id = update.message.chat_id
    try:
        chat[chat_id]
    except KeyError:
        bot.sendMessage(chat_id, text='Error! Please initialize the bot with /start.')
    else:
        chat[chat_id].newevent(bot, update)
        dp.addTelegramMessageHandler(chat[chat_id].newevent2)
        dp.addTelegramMessageHandler(chat[chat_id].settitle2)
        dp.addTelegramMessageHandler(chat[chat_id].setschedule2)
        try:
            chat[chat_id.schedule]
        except AttributeError:
            pass
        else:
            for x in range(1, len(chat[chat_id].schedule)+1):
                dp.removeTelegramCommandHandler(str(x), chat[chat_id].selectoption)
            dp.removeTelegramMessageHandler(chat[chat_id].set_date)
            dp.removeTelegramMessageHandler(chat[chat_id].set_date2)
            dp.removeTelegramMessageHandler(chat[chat_id].setschedule2)
            dp.removeTelegramMessageHandler(chat[chat_id].display_voting)


def schedule(bot, update):
    chat_id = update.message.chat_id
    try:
        chat[chat_id]
    except KeyError:
        bot.sendMessage(chat_id, text='Error! Please initialize the bot with /start.')
    else:
        dp.removeTelegramMessageHandler(chat[chat_id].newevent2)
        dp.removeTelegramMessageHandler(chat[chat_id].settitle2)
        chat[chat_id].setschedule(bot, update)
        dp.addTelegramMessageHandler(chat[chat_id].setschedule2)


def done(bot, update):
    chat_id = update.message.chat_id
    dp.removeTelegramMessageHandler(chat[chat_id].newevent2)
    dp.removeTelegramMessageHandler(chat[chat_id].settitle2)
    dp.removeTelegramMessageHandler(chat[chat_id].setschedule2)
    chat[chat_id].setup_complete(bot, update)
    dp.addTelegramMessageHandler(chat[chat_id].display_voting)
    chat[chat_id].display_voting(bot, update)
    # We add 1 to the length of the schedule dictionary for list comprehension.
    for i in range(1, len(chat[chat_id].schedule)+1):
        dp.addTelegramCommandHandler(str(i), chat[chat_id].selectoption)


def event(bot, update):
    chat_id = update.message.chat_id
    try:
        chat[chat_id]
    except KeyError:
        bot.sendMessage(chat_id, text='Error! Please initialize the bot with /start.')
    else:
        chat[chat_id].display_voting(bot, update)


def results(bot, update):
    chat_id = update.message.chat_id
    try:
        chat[chat_id]
    except KeyError:
        bot.sendMessage(chat_id, text='Error! Please initialize the bot with /start.')
    else:
        chat[chat_id].viewresults(bot, update)


def finish(bot, update):
    chat_id = update.message.chat_id
    try:
        chat[chat_id]
    except KeyError:
        bot.sendMessage(chat_id, text='Error! Please initialize the bot with /start.')
    else:
        dp.removeTelegramMessageHandler(chat[chat_id].display_voting)
        chat[chat_id].finishvoting(bot, update)
        dp.addTelegramMessageHandler(chat[chat_id].set_date)
        dp.addTelegramMessageHandler(chat[chat_id].set_date2)
        for i in range(1, len(chat[chat_id].schedule)+1):
            dp.removeTelegramCommandHandler(str(i), chat[chat_id].selectoption)


def debug(bot, update):
    # Temporary /debug command for testing the /results command.
    print('[DEBUG] Launching developer debug run...')
    chat_id = update.message.chat_id
    chat[chat_id] = Chat(chat_id)
    chat[chat_id].init_complete(bot)
    chat[chat_id].event_title = 'Testing Bot Event'
    chat[chat_id].schedule = {'1 Jan': ['Shing', 'Daniel', 'Jess', 'Anna'], '2 Jan': ['Jess', 'Anna'],
                              '3 Jan': ['Shing', 'Daniel'], '4 Jan': ['Shing', 'Jess', 'Anna'],
                              '5 Jan': ['Daniel']}
    chat[chat_id].schedule_keys = ['1 Jan', '2 Jan', '3 Jan', '4 Jan', '5 Jan']
    chat[chat_id].schedule_alt = '/1: 1 Jan\n/2: 2 Jan\n/3: 3 Jan\n/4: 4 Jan\n/5: 5 Jan\n'
    chat[chat_id].input_title = False
    chat[chat_id].input_schedule = False
    chat[chat_id].accept_votes = True
    chat[chat_id].viewresults(bot, update)


def any_message(bot, update):
    logger.info("New message from: %s | chat_id: %d | Text: %s" %
                (update.message.from_user.username, update.message.chat_id, update.message.text))


def unknown_command(bot, update):
    # Answer in Telegram
    bot.sendMessage(update.message.chat_id, text='Command not recognized! You can try /start.')


def error(bot, update, error):
    # Print error to console
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    # Slash command handlers here.
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("newevent", newevent)
    dp.addTelegramCommandHandler("schedule", schedule)
    dp.addTelegramCommandHandler("done", done)
    dp.addTelegramCommandHandler("event", event)
    dp.addTelegramCommandHandler("results", results)
    dp.addTelegramCommandHandler("finish", finish)

    # For Your Eyes Only.
    dp.addTelegramCommandHandler("debug", debug)

    # All other handlers here.
    dp.addUnknownTelegramCommandHandler(unknown_command)
    dp.addTelegramRegexHandler('.*', any_message)
    dp.addErrorHandler(error)

    # Start the Bot.
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
