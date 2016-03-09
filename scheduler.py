# Shing's Telegram Scheduler Bot
# Backend to define classes and logic.
# First time trying to separate a program into a framework. Expect lots of debugging.


import telegram


# Just so I can see where it starts...
print('[DEBUG] BACKEND STARTED AND OPERATIONAL!')


# Define some styles for shorter form and easier reference.
fr = telegram.ForceReply(selective=True)
hide = telegram.ReplyKeyboardHide()


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
        voters: Placeholder for all unique voters. Default empty string.
        results: Placeholder for results. Default empty string.
        best_date: Placeholder for recommended date. Default empty list.
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
        self.voters = []
        self.results = ''
        self.best_date = []

    def init_complete(self, bot):
        if not self.chat_id == '':
            print('[DEBUG %i] Chat initialized and recognised by program. Hello World!' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Hello and welcome to Shing\'s scheduler bot!\n'
                                                                  'You can create a new event with /newevent.')
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
        if self.input_title:
            self.new_title = update.message.text
            self.title = self.new_title
            self.input_title = False
            print('[DEBUG %i] %s set new title.' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Title set to \"%s\".' % self.title)
            bot.sendMessage(self.chat_id, text='Please use /schedule to begin setting choices.')

    def setschedule(self, bot, update):
        # Prepare to receive a new schedule for event.
        if not self.schedule:
            self.input_schedule = True
            print('[DEBUG %i] %s begins to create schedule...' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                            text='Please set a possible meeting date/time for %s.' % self.title)
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
        self.new_schedule = update.message.text
        self.schedule[self.new_schedule] = []
        self.schedule_keys.append(self.new_schedule)
        print('[DEBUG %i] setschedule2 registered an option.' % self.chat_id)
        bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                        text='Option registered. Send another option, or type /done to publish.')

    def setup_complete(self, bot, update):
        # Finish setting up the event. Activate the bot to take votes.
        self.input_schedule = False
        # Set up list of voting possibilities.
        i = 0
        for n in self.schedule_keys:
            i += 1
            self.schedule_alt += ('/' + str(i) + ': ' + str(n) + '\n')
            self.schedule[n] = []
        print('[DEBUG %i] List of Options:\n%s' % (self.chat_id, self.schedule_alt))
        self.accept_votes = True
        print('[DEBUG %i] Event successfully set up by %s.' % (self.chat_id, update.message.from_user.first_name))
        print('[DEBUG %i] Now accepting votes...' % self.chat_id)
        bot.sendMessage(self.chat_id, reply_markup=hide, text='Schedule and poll created successfully.')

    def display_voting(self, bot):
        # TODO: Markup keyboard buttons for voting.
        if self.accept_votes:
            print('[DEBUG %i] Chat requested poll to be posted.' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_markup=fr,
                            text='[NEW EVENT]\n%s\n'
                                 'Please state your availability for the below dates:\n%s\n'
                                 'You can vote for as many dates as you can attend.\n'
                                 'You can cancel your vote for a date by voting twice on the date.\n\n'
                                 'Send /results to view the current poll standings.'
                                 % (self.title, self.schedule_alt))

    def selectoption(self, bot, update):
        # Translate the slash command back into the key to match to the dict.
        # For x, we subtract 1 to match list logic which starts at 0.
        x = int(update.message.text[1:]) - 1
        self.option = self.schedule_keys[x]
        print('[DEBUG %i] Testing option selected is %s.' % (self.chat_id, self.option))
        # Check if name already in the selected key. If so, remove the name.
        if update.message.from_user.first_name in self.schedule[self.option]:
            self.schedule[self.option].remove(update.message.from_user.first_name)
            print('[DEBUG %i] Name already exists in key. Removing...' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Existing entry found. You are unavailable for %s.' % self.option)
        else:
            self.schedule[self.option].append(update.message.from_user.first_name)
            print('[DEBUG %i] Name does not exist in key. Adding...' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Response received. You are available for %s.' % self.option)

    def viewresults(self, bot, update):
        # View results at the current point of time.
        # Use a loop to go through keys and print out each person available.
        print('[DEBUG %i] Results for Event requested. Sending to Chat...' % self.chat_id)
        mostvotes = 0
        for n in self.schedule_keys:
            i = ', '.join(str(p) for p in self.schedule[n])
            self.results += (str(n) + ' - ' + str(len(self.schedule[n])) + ' available\n' + i + '\n\n')
            # For each iteration, check if it is the one with most votes.
            # If so, set is as the best date. If it is a tie, add it to the best date list.
            if len(self.schedule[n]) > mostvotes and len(self.schedule[n]) != 0:
                mostvotes = len(self.schedule[n])
                self.best_date = []
                self.best_date.append(n)
            elif len(self.schedule[n]) == mostvotes and len(self.schedule[n]) != 0:
                self.best_date.append(n)
        # Find the key with the highest number (beware of ties), then post results to chat.
        if len(self.best_date) == 1:
            r = 'Recommended date for your event: ' + str(self.best_date[0])
            print('[DEBUG %i] Results sent.' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Results for Event: %s\n\n%s%s' % (self.title, self.results, r))
        elif len(self.best_date) > 1:
            b = ', '.join(str(p) for p in self.best_date)
            r = 'Multiple dates found. Recommended dates for your event: ' + str(b)
            print('[DEBUG %i] Results sent.' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Results for Event: %s\n\n%s%s' % (self.title, self.results, r))
