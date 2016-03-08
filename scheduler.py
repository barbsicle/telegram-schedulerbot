# Shing's Telegram Scheduler Bot
# Backend to define classes and logic.
# First time trying to separate a program into a framework. Expect lots of debugging.


import telegram


# Just so I can see where it starts...
print('[DEBUG] BACKEND STARTED AND OPERATIONAL!')


# Define some styles for shorter form and easier reference.
fr = telegram.ForceReply(selective=True)


# Define a chat and initialize variables.
class Chat(object):
    """A telegram chat that has used the /start command.

    Attributes
        id: ID of chat. Can take on negative number.
        title: Name of event. Default empty string.
        schedule: Date(s) and time(s) of event. Default empty dict.
        schedule_keys: List containing all keys of schedule. Default empty list.
        schedule_alt: Printable version of schedule. Default empty string.
        input_title: Switch for inputting event title. Default False.
        input_schedule: Switch for inputting schedule. Default False.
        accept_votes: Switch to begin accepting votes. Default False.
        new_title: Placeholder for new title.
        new_schedule: Placeholder for new keys to be added into the schedule dict.
        option: Placeholder for option voted on.
    """

    def __init__(self, chat_id):
        # Initializing new chat variables.
        self.chat_id = chat_id
        self.title = ''
        self.schedule = {}
        self.schedule_keys = []
        self.schedule_alt = ''
        self.input_title = False
        self.input_schedule = False
        self.accept_votes = False
        self.new_title = ''
        self.new_schedule = ''
        self.option = 0

    def init_complete(self, bot):
        if not self.chat_id == '':
            print('[DEBUG %i] Chat initialized and recognised by program. Hello World!' % self.chat_id)
            bot.sendMessage(self.chat_id, text='Hello and welcome to Shing\'s scheduler bot!\n'
                                               'You can create a new event with /new.')
        else:
            exit('[DEBUG] Something went wrong and chat was not initialized. Please investigate.')

    def newevent(self, bot, update):
        if not self.input_title and self.title == '':
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='New event requested. Please follow the instructions below...')

    def settitle(self, bot, update):
        # Prepare to receive new title for event.
        if not self.input_title and self.title == '':
            self.input_title = True
            print('[DEBUG %i] %s began setting new title.' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_markup=fr, text='Please set the title of your event.\n')
        elif not self.input_title:
            self.input_title = True
            print('[DEBUG %i] %s began re-setting new title.' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_markup=fr, text='Please re-set the title of your event.\n')

    def settitle2(self, bot, update):
        # When initialized, replies to settitle messages will trigger a change in the title.
        self.new_title = update.message.text
        self.title = self.new_title
        self.input_title = False
        print('[DEBUG %i] %s set new title.' % (self.chat_id, update.message.from_user.first_name))
        bot.sendMessage(self.chat_id, text='Title set to \"%s\".' % self.title)
        bot.sendMessage(self.chat_id, text='Please use /schedule to begin setting choices.')

    def setschedule(self, bot, update):
        # Prepare to receive a new schedule for event.
        if not self.schedule:
            self.input_schedule = True
            print('[DEBUG %i] %s begins to create schedule...' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                            text='Please set the first date/time to meet for %s.' % self.title)
        # TODO: More control over modification of schedule.
        elif self.schedule:
            self.input_schedule = True
            print('[DEBUG %i] %s begins to remake schedule...' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Schedule reset. Please restart the schedule creation.\n'
                                 'Please set the first date/time to meet for %s.' % self.title)

    def setschedule2(self, bot, update):
        # When initialized, replies to setschedule messages will add new keys to the schedule dictionary.
        # TODO: Check if while loop stops the updater.
        print('[DEBUG %i] setschedule2 is operational.' % self.chat_id)
        self.new_schedule = update.message.text
        self.schedule[self.new_schedule] = []
        self.schedule_keys.append(self.new_schedule)
        print('[DEBUG %i] setschedule2 registered an option.' % self.chat_id)
        bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                        text='Option registered. Send another option, or send /done to publish.')

    def setup_complete(self, bot, update):
        # Finish setting up the event. Activate the bot to take votes.
        self.input_schedule = False
        # Set up list of voting possibilities.
        i = 0
        for n in self.schedule_keys:
            i += 1
            self.schedule_alt += ('\n/' + str(i) + ': ' + str(n))
        print('[DEBUG %i] List of Options:%s' % (self.chat_id, self.schedule_alt))
        self.accept_votes = True
        print('[DEBUG %i] Event successfully set up by %s.' % (self.chat_id, update.message.from_user.first_name))
        bot.sendMessage(self.chat_id, text='Schedule and poll created successfully.')

    def display_voting(self, bot):
        if self.accept_votes:
            print('[DEBUG %i] Now accepting votes...' % self.chat_id)
            bot.sendMessage(self.chat_id, text='[NEW EVENT]\n%s\n'
                                               'Please state your availability for the below dates:%s\n'
                                               'You can cancel your vote for a date by voting twice on the date.' %
                                               (self.title, self.schedule_alt))

    def selectoption(self, bot, update):
        # Translate the slash command back into the key to match to the dict.
        # TODO: x doesn't work. Needs another method.
        x = int(int(s) for s in update.message.text.split() if s.isdigit())
        self.option = self.schedule_keys[x]
        print('[DEBUG %i] Testing option selected is %s.' % (self.chat_id, self.option))
        # Check if name already in the selected key. If so, remove the name.
        if update.message.from_user.first_name in self.schedule[self.option]:
            self.schedule[self.option].remove(update.message.from_user.first_name)
            print('[DEBUG %i] Name already exists in key. Removing...' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Existing entry found and removed from %s' % self.option)
        else:
            self.schedule[self.option].append(update.message.from_user.first_name)
            print('[DEBUG %i] Name does not exist in key. Adding...' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Response received for %s' % self.option)
