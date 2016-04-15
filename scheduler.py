# Shing's Telegram Scheduler Bot
# Backend to define classes and logic.
# First time trying to separate a program into a framework. Expect lots of debugging.


import telegram


# Define some styles for shorter form and easier reference.
fr = telegram.ForceReply(selective=True)
hide = telegram.ReplyKeyboardHide()


# Define a chat and initialize variables.
class Chat(object):
    """A telegram chat that has used the /start command.

    Attributes
        id: ID of chat. Can take on negative number.
        title: Title of chat (if group chat).
        size: Number of members in this chat.
        event_title: Name of event. Default empty string.
        event_date: Final date set for event. Objective of the entire program! Default empty string.
        schedule: Date(s) and time(s) of event. Default empty dict.
        schedule_keys: List containing all keys of schedule. Default empty list.
        schedule_alt: Printable version of schedule. Default empty string.
        remake_event: Switch for remaking event. Default False.
        input_title: Switch for inputting event title. Default 0.
        input_schedule: Switch for inputting schedule. Default False.
        accept_votes: Switch to begin accepting votes. Default False.
        finalize_date: Switch to begin finalizing of date. Default 0.
        custom_keyboard: Placeholder for custom keyboards. Default empty list.
        new_event_title: Placeholder for new event title.
        new_schedule: Placeholder for new keys to be added into the schedule dict.
        option: Placeholder for option voted on.
        voters: Placeholder for all unique voters. Default empty string.
        results: Placeholder for results. Default empty string.
        best_date: Placeholder for recommended date. Default empty list.
    """

    def __init__(self, chat_id):
        # Initializing new chat variables.
        self.chat_id = chat_id
        self.size = telegram.Chat(chat_id, 'group')
        self.event_title = ''
        self.event_date = ''
        self.schedule = {}
        self.schedule_keys = []
        self.schedule_alt = ''
        self.remake_event = False
        self.input_title = 0
        self.input_schedule = False
        self.accept_votes = False
        self.finalize_date = 0
        self.custom_keyboard = []
        self.new_event_title = ''
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

    def init_restart(self, bot):
        # Activated when /start is used after the first time to reset the bot.
        print('[DEBUG %i] Chat is now reset with /start.' % self.chat_id)
        self.__init__(self.chat_id)
        self.init_complete(bot)

    def newevent(self, bot, update):
        if self.input_schedule:
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Please wait till the schedule is created before trying other commands!')
        elif self.input_title == 0 and self.event_title == '':
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                            text='New event requested...\nPlease set the title of your event.')
            self.settitle(bot, update)
        elif self.input_title == 0 and self.finalize_date == 3:
            print('[DEBUG %i] Deleting old (scheduled) event and restarting...' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                            text='New event requested...\nPlease set the title of your event.')
            self.__init__(self.chat_id)
            self.settitle(bot, update)
        elif self.input_title == 0 and self.event_title != '':
            self.remake_event = True
            self.custom_keyboard = [['Yes', 'No']]
            reply_markup = telegram.ReplyKeyboardMarkup(self.custom_keyboard)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=reply_markup,
                            text='Event creation already in progress!\n'
                                 'Are you sure you want to proceed with creating a new event?')

    def newevent2(self, bot, update):
        if self.remake_event and update.message.text == 'Yes':
            print('[DEBUG %i] newevent2 triggered.' % self.chat_id)
            self.remake_event = False
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Deleting old event and starting over...')
            self.__init__(self.chat_id)
            self.settitle(bot, update)
        elif self.remake_event and update.message.text == 'No':
            print('[DEBUG %i] newevent2 triggered.' % self.chat_id)
            self.remake_event = False
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                            text='Reverting back to normal parameters...')

    def settitle(self, bot, update):
        # TODO: Change the %s call to a reply message.
        # Prepare to receive new title for event.
        if self.input_title == 0 and self.event_title == '':
            self.input_title = 1
            print('[DEBUG %i] %s began setting new title.' % (self.chat_id, update.message.from_user.first_name))
        elif self.input_title == 0 and self.event_title != '':
            self.input_title = 2
            print('[DEBUG %i] %s began re-setting new title.' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_markup=fr, text='Please re-set the title of your event.\n')
        else:
            exit('[DEBUG %i] Error. Please debug.' % self.chat_id)

    def settitle2(self, bot, update):
        # When initialized, replies to settitle messages will trigger a change in the title.
        if self.input_title != 0:
            print('[DEBUG %i] settitle2 triggered.' % self.chat_id)
            self.new_event_title = update.message.text
            self.event_title = self.new_event_title
            print('[DEBUG %i] %s set new title.' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Title set to \"%s\".' % self.event_title)
            if self.input_title == 1:
                self.input_title = 0
                self.setschedule(bot, update)
            else:
                self.input_title = 0

    def setschedule(self, bot, update):
        # Prepare to receive a new schedule for event.
        if self.event_title != '':
            if not self.schedule:
                self.input_schedule = True
                print('[DEBUG %i] %s begins to create schedule...' %
                      (self.chat_id, update.message.from_user.first_name))
                bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                                text='Please set the possible meeting date(s) or time(s) for your event.')
            # TODO: More control over modification of schedule.
            elif self.schedule:
                self.input_schedule = True
                print('[DEBUG %i] %s begins to remake schedule...' %
                      (self.chat_id, update.message.from_user.first_name))
                bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                                text='Schedule reset. Please restart the schedule creation.\n'
                                     'Please set the possible meeting date(s) or time(s) for your event.')
        elif self.event_title == '':
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Error! Event title is not yet created.\n'
                                                                  'Try using /newevent to create a new event.')

    def setschedule2(self, bot, update):
        # When initialized, replies to setschedule messages will add new keys to the schedule dictionary.
        if self.input_schedule and update.message.text != self.event_title:
            self.new_schedule = update.message.text
            print('[DEBUG %i] setsachedule2 triggered.' % self.chat_id)
            if self.new_schedule in self.schedule_keys:
                self.schedule.pop(self.new_schedule, None)
                self.schedule_keys.remove(self.new_schedule)
                print('[DEBUG %i] Identical option set. Removing..' % self.chat_id)
                bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                                text='Option already exists. It has been removed.\n'
                                     'If you want to remove an option, just repeat your message.\n'
                                     'Please send another option or type /done to publish.')
            else:
                self.schedule[self.new_schedule] = []
                self.schedule_keys.append(self.new_schedule)
                print('[DEBUG %i] Chat registered an option.' % self.chat_id)
                bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                                text='Option registered.\n'
                                     'If you want to remove an option, just repeat your message.\n'
                                     'Please send another option, or type /done to publish.')

    def setup_complete(self, bot, update):
        # Finish setting up the event. Activate the bot to take votes.
        self.input_schedule = False
        # Set up list of voting possibilities.
        i = 0
        self.custom_keyboard.append([])
        for n in self.schedule_keys:
            i += 1
            self.custom_keyboard[0].append('/'+str(i))
            self.schedule_alt += ('/' + str(i) + ': ' + str(n) + '\n')
            self.schedule[n] = []
        print('[DEBUG %i] List of Options:\n%s' % (self.chat_id, self.schedule_alt))
        self.accept_votes = True
        print('[DEBUG %i] Event successfully set up by %s.' % (self.chat_id, update.message.from_user.first_name))
        print('[DEBUG %i] Now accepting votes...' % self.chat_id)
        bot.sendMessage(self.chat_id, reply_markup=hide, text='Schedule and poll created successfully.')

    def display_voting(self, bot, update):
        if self.accept_votes:
            reply_markup = telegram.ReplyKeyboardMarkup(self.custom_keyboard)
            print('[DEBUG %i] Chat requested poll to be posted.' % self.chat_id)
            bot.sendMessage(self.chat_id, reply_markup=reply_markup,
                            text='[NEW EVENT]\n%s\n'
                                 'Please state your availability for the below dates:\n%s\n'
                                 'You can vote for as many dates as you can attend.\n'
                                 'You can cancel your vote for a date by voting twice on the date.\n\n'
                                 'Send /event to repeat the current event\n'
                                 'Send /results to view the current availability roster (and check your votes).\n'
                                 'Send /finish to close voting and set a date for the event.'
                                 % (self.event_title, self.schedule_alt))
        elif not self.accept_votes:
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Error! The poll is not yet created.')

    def selectoption(self, bot, update):
        # TODO: Make this less messy (already removed print to chat).
        # Translate the slash command back into the key to match to the dict.
        # For x, we subtract 1 to match list logic which starts at 0.
        x = int(update.message.text[1:]) - 1
        self.option = self.schedule_keys[x]
        print('[DEBUG %i] Testing option selected is %s.' % (self.chat_id, self.option))
        # Check if name already in the selected key. If so, remove the name.
        if update.message.from_user.first_name in self.schedule[self.option]:
            self.schedule[self.option].remove(update.message.from_user.first_name)
            print('[DEBUG %i] Name already exists in key. Removing...' % self.chat_id)
            # bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
            #                 text='Existing entry found. You are unavailable for %s.' % self.option)
        else:
            self.schedule[self.option].append(update.message.from_user.first_name)
            print('[DEBUG %i] Name does not exist in key. Adding...' % self.chat_id)
            # bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
            #                 text='Response received. You are available for %s.' % self.option)

    def viewresults(self, bot, update):
        # View results at the current point of time.
        # Use a loop to go through keys and print out each person available.
        if self.accept_votes:
            print('[DEBUG %i] Results for Event requested. Sending to Chat...' % self.chat_id)
            mostvotes = 0
            self.custom_keyboard = []
            for n in self.schedule_keys:
                self.schedule[n] = sorted(self.schedule[n], key=str.lower)
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
                                text='Results for Event: %s\n\n%s%s\n'
                                     'Use /finish to finish voting and decide.' % (self.event_title, self.results, r))
                # Reset results list so that it does not repeat itself.
                self.results = ''
            elif len(self.best_date) > 1:
                b = ', '.join(str(p) for p in self.best_date)
                r = 'Multiple dates found for your event.\nRecommended dates: ' + str(b)
                print('[DEBUG %i] Results sent.' % self.chat_id)
                bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id,
                                text='Results for Event: %s\n\n%s%s\n'
                                     'Use /finish to finish voting and decide.' % (self.event_title, self.results, r))
                # Reset results list so that it does not repeat itself.
                self.results = ''
        elif not self.accept_votes:
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Error! The poll is not yet created.')

    def finishvoting(self, bot, update):
        # Close voting, show results, and request for final date
        if self.accept_votes:
            self.viewresults(bot, update)
            self.accept_votes = False
            print('[DEBUG %i] Voting for event concluded.' % self.chat_id)
            self.finalize_date = 1
            self.custom_keyboard.append(self.best_date)
            self.custom_keyboard[0].append('CUSTOM DATE')
            reply_markup = telegram.ReplyKeyboardMarkup(self.custom_keyboard)
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=reply_markup,
                            text='Please input your final choice of date/time for the event.')
            if 'CUSTOM DATE' in self.best_date:
                self.best_date.remove('CUSTOM DATE')
        elif not self.accept_votes:
            bot.sendMessage(self.chat_id, reply_markup=hide, text='Error! The poll is not yet created.')

    def set_date0(self, bot, update):
        print('[DEBUG %i] Date set for event.' % self.chat_id)
        self.finalize_date = 3
        old_title = update.message.chat.title
        if old_title == '':
            # Chat using bot is a one-to-one; scheduler is quite useless like this.
            bot.sendMessage(self.chat_id, reply_markup=hide,
                            text='%s will be happening on %s!\n'
                                 'But you are in a personal chat...\n'
                                 'Please try to schedule an event with some friends!' %
                                 (self.event_title, self.event_date))
        else:
            bot.sendMessage(self.chat_id, reply_markup=hide, text='%s will be happening on %s!\n'
                                                                  'Please paste the following as your chat title: ' %
                                                                  (self.event_title, self.event_date))
            bot.sendMessage(self.chat_id, text='%s - %s @ %s' % (old_title, self.event_title, self.event_date))
            bot.sendMessage(self.chat_id, text='Thanks for using Scheduler Bot!\n'
                                               'You can use /newevent to start scheduling another event!')

    def set_date(self, bot, update):
        # Set date for the event and lock it in.
        if self.finalize_date == 1 and update.message.text in self.best_date:
            self.event_date = update.message.text
            self.set_date0(bot, update)
        if self.finalize_date == 1 and update.message.text == 'CUSTOM DATE':
            self.finalize_date = 2
            print('[DEBUG %i] %s is setting a custom date.' % (self.chat_id, update.message.from_user.first_name))
            bot.sendMessage(self.chat_id, reply_to_message_id=update.message.message_id, reply_markup=fr,
                            text='[EVENT CLOSED] No more voting!\n'
                                 'Please type the custom date and time you would like to set.')

    def set_date2(self, bot, update):
        if self.finalize_date == 2 and update.message.text != 'CUSTOM DATE':
            bot.sendMessage(self.chat_id, text='Sorry everyone, but the vote was in vain :(')
            self.event_date = update.message.text
            self.set_date0(bot, update)
