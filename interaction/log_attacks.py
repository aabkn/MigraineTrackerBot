from config.config import States, LogStep, attack_start_dict, n_attack_days
import datetime
from config import keyboards
from migraine_bot import db, bot


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hey, I am a bot for tracking migraines! Here is the list of "
                     "the possible commands:\n/log - log a running attack"
                     "\n/cancel - cancel a logging "
                     "\n/edit - edit a logged attack "
                     "\n/stats - get .csv file of logged attacks "
                     "\n/calendar - get a month calendar of past attacks along with their intensities "
                     "\n/help - get list of possible commands"
                     "\nNow let's know each other. What's your name?",
                     reply_markup=keyboards.remove_keyboard)

    db.set_state(message.chat.id, States.WELCOME)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Hey, I am a bot for tracking migraines! Here is the list of "
                     "the possible commands:\n/log - log a running attack "
                     "\n/cancel - cancel a logging "
                     "\n/edit - edit a logged attack "
                     "\n/stats - get .csv file of logged attacks"
                     "\n/calendar - get a month calendar of past attacks along with their intensities "
                     "\n/help - get list of possible commands")


@bot.message_handler(commands=['cancel'])
def cancel_log(message):
    chat_id = message.chat.id
    state = db.get_state(chat_id)
    db.set_step(chat_id, LogStep.INACTIVE)
    if state in [States.INACTIVE, States.WELCOME]:
        bot.reply_to(message, "Nothing to cancel. If you want to log an attack, just use commands /log to log "
                              "an attack.",
                     reply_markup=keyboards.remove_keyboard)
        return

    if state == States.LOGGING:
        db.delete_current_log(chat_id)
        db.set_state(chat_id, States.INACTIVE)
        bot.reply_to(message, "OK, I cancelled this log. If you want to log an attack, just use commands /log to log "
                              "an attack.",
                     reply_markup=keyboards.remove_keyboard)
    if state == States.STATS:
        db.set_state(chat_id, States.INACTIVE)
        bot.reply_to(message, "OK, I cancelled this operation. If you want to get statistics, just use commands /stats"
                              " to get .csv file and /calendar to get a calendar of past attacks along"
                              " with their intensities",
                     reply_markup=keyboards.remove_keyboard)
    if state == States.EDITING:
        db.delete_current_log(chat_id)
        db.set_state(chat_id, States.INACTIVE)
        bot.reply_to(message, "OK, I cancelled editing. If you want to edit an attack, just use commands /edit",
                     reply_markup=keyboards.remove_keyboard)


@bot.message_handler(commands=['log'])
def start_log(message):
    chat_id = message.chat.id
    name = db.get_username(chat_id)
    if db.get_state(chat_id) == States.LOGGING:
        bot.reply_to(message, "I've already started logging. If you want to cancel, just use /cancel.")
        return
    bot.reply_to(message, f'Hi, {name}! You started to log a migraine attack.\nSorry to hear that! '
                          f'When was the attack? You can choose one of the listed options or '
                          f'enter the date in the format dd-mm-yy',
                 reply_markup=keyboards.date_keyboard)

    db.set_step(chat_id, LogStep.DATE)
    db.set_state(chat_id, States.LOGGING)


@bot.message_handler(commands=['edit'])
def start_edit(message):
    chat_id = message.chat.id
    step = db.get_step(chat_id)
    state = db.get_state(chat_id)

    if (state == States.EDITING) and (message.text == '/edit'):
        bot.send_message(chat_id, "I've already started editing. If you want to cancel, use /cancel.")
    elif state == States.LOGGING:
        if step == LogStep.ATTACK_START:
            bot.send_message(chat_id, 'Ok, let\'s edit the location of pain. Just choose the correct option',
                             reply_markup=keyboards.location_keyboard)
            db.set_step(chat_id, LogStep.LOCATION)
        elif step == LogStep.LOCATION:
            bot.send_message(chat_id, 'You can now tell a correct value of the pain level from 0 to 10',
                             reply_markup=keyboards.intensity_keyboard)
            db.set_step(chat_id, LogStep.INTENSITY)
        elif step == LogStep.INTENSITY:
            bot.send_message(chat_id, 'Please, choose now the correct option or enter the date in the format dd-mm-yy',
                             reply_markup=keyboards.date_keyboard)
            db.set_step(chat_id, LogStep.DATE)
    elif step == LogStep.FINISH_LOG:
        db.set_state(chat_id, States.EDITING)
        db.set_step(chat_id, LogStep.CHOOSE_EDIT)
        db.fetch_last_log(chat_id)
        bot.send_message(chat_id, 'What would you like to edit?',
                         reply_markup=keyboards.edit_keyboard)
    else:
        past_attacks_keyboard = keyboards.create_keyboard(options=db.get_last_dates(chat_id, n_attack_days))
        bot.send_message(chat_id, f'Please choose the date of an attack you would like to edit. Here are '
                                  f'{n_attack_days} dates of your most recent attacks.\n\n You can choose one of the'
                                  f' listed options or type the date in the format dd-mm-yy.',
                         reply_markup=past_attacks_keyboard)
        db.set_step(chat_id, LogStep.CHOOSE_ATTACK)
        db.set_state(chat_id, States.EDITING)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.EDITING)
def edit(message):
    chat_id = message.chat.id
    step = db.get_step(chat_id)
    if step == LogStep.INTENSITY:
        process_intensity(message)
    elif step == LogStep.ATTACK_START:
        process_pain_start(message)
    elif step == LogStep.LOCATION:
        process_side(message)
    elif step == LogStep.DATE:
        process_date(message)
    elif step == LogStep.CHOOSE_EDIT:
        chosen_option = message.text
        if not(chosen_option.lower() in ['intensity', 'pain location', 'pain start', 'side', 'location',
                                         'start', 'date', 'edit another attack']):
            bot.send_message(chat_id, 'Please, choose one of the listed options')
        else:
            if chosen_option.lower() in ['intensity']:
                bot.send_message(chat_id, 'You can now tell a correct value of the pain level from 0 to 10',
                                 reply_markup=keyboards.intensity_keyboard)
                db.set_step(chat_id, LogStep.INTENSITY)

            elif chosen_option.lower() in ['pain location', 'side', 'location']:
                bot.send_message(chat_id, 'Ok, let\'s edit the location of pain. Just choose the correct option',
                                 reply_markup=keyboards.location_keyboard)
                db.set_step(chat_id, LogStep.LOCATION)
            elif chosen_option.lower() in ['start', 'pain start']:
                bot.send_message(chat_id, 'Now you can edit the start of the attack. Please, choose the correct option',
                                 reply_markup=keyboards.pain_start_keyboard)
                db.set_step(chat_id, LogStep.ATTACK_START)
            elif chosen_option.lower() in ['date']:
                bot.send_message(chat_id, 'Please, choose now the matching option or enter the'
                                          ' date in the format dd-mm-yy',
                                 reply_markup=keyboards.date_keyboard)
                db.set_step(chat_id, LogStep.DATE)
            else:
                db.set_step(chat_id, LogStep.CHOOSE_ATTACK)
                db.delete_current_log(chat_id)
                start_edit(message)
    elif step == LogStep.CHOOSE_ATTACK:
        date_str = message.text
        if date_str in db.get_last_dates(chat_id, n_attack_days):
            date = datetime.datetime.strptime(date_str, '%d %b %Y')
        else:
            try:
                date = datetime.datetime.strptime(date_str, '%d-%m-%y')
            except ValueError:
                bot.send_message(chat_id, 'Please, choose one of the options or enter the date in the format'
                                          ' dd-mm-yy', reply_markup=keyboards.date_keyboard)
                return
        logs_date = db.get_log(chat_id, date)
        if len(logs_date) == 1:
            message = print_log(chat_id, logs_date[0])
            bot.send_message(chat_id, 'Here are the details of the attack for the chosen date:\n' + message +
                             'What would you like to edit?', reply_markup=keyboards.edit_keyboard)
            db.set_step(chat_id, LogStep.CHOOSE_EDIT)
        elif len(logs_date) == 0:
            bot.send_message(chat_id, 'There are no attacks for the chosen date. Please choose another date from the '
                                      'listed options or enter the date in the format dd-mm-yy',
                             reply_markup=keyboards.create_keyboard(options=db.get_last_dates(chat_id, n_attack_days)))
        else:
            message = ''
            for i, migraine_log in enumerate(logs_date):
                message += f'{i + 1}. ' + print_log(chat_id, migraine_log) + '\n'
            bot.send_message(chat_id, "For the chosen date there are multiple attacks, here are the details.\n\n" +
                             message + " Please choose the number of an attack you'd like to edit",
                             reply_markup=keyboards.create_keyboard(range(1, 1 + len(logs_date))))
            db.set_step(chat_id, LogStep.CHOOSE_ATTACK_MULTIPLE)

    elif step == LogStep.CHOOSE_ATTACK_MULTIPLE:
        try:
            attack_num = int(message.text) - 1
            if db.keep_one_log(chat_id, attack_num) == -1:
                bot.reply_to(message, 'The entered number is too big or too small. '
                                      '\nPlease choose the number of an attack you want to edit.')
                return
            bot.send_message(chat_id, 'Got it. What would you like to edit?',
                             reply_markup=keyboards.edit_keyboard)
            db.set_step(chat_id, LogStep.CHOOSE_EDIT)
        except ValueError:
            bot.reply_to(message, 'Please choose the valid integer number.')


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.WELCOME)
def process_name(message):
    chat_id = message.chat.id
    name = message.text
    db.insert_user(chat_id, name)

    bot.reply_to(message, f'Nice to meet you, {name}!', reply_markup=keyboards.remove_keyboard)
    db.set_state(chat_id, States.INACTIVE)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.LOGGING)
def log(message):
    step = db.get_step(message.chat.id)
    if step == LogStep.DATE:
        process_date(message)
    elif step == LogStep.INTENSITY:
        process_intensity(message)
    elif step == LogStep.ATTACK_START:
        process_pain_start(message)
    elif step == LogStep.LOCATION:
        process_side(message)


def process_date(message):
    chat_id = message.chat.id
    date = message.text
    date_options = keyboards.date_options(datetime.date.today())
    if date in date_options:
        days_delta = date_options.index(date)
        attack_date = datetime.date.today() - datetime.timedelta(days=days_delta)
        attack_date = datetime.datetime(attack_date.year, attack_date.month, attack_date.day)
    else:
        try:
            attack_date = datetime.datetime.strptime(date, '%d-%m-%y')
        except ValueError:
            bot.reply_to(message, "I can't interpret your answer as a date. "
                                  "Please, enter the date in the format dd-mm-yy or choose one of the listed options.")
    db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'date': attack_date}})

    if db.get_state(chat_id) == States.LOGGING:
        db.set_step(chat_id, LogStep.INTENSITY)
        bot.send_message(chat_id, "How would you estimate intensity of the pain from 0 to 10? You might want to use "
                                  "the suggested keyboard or type any numeric value from 0 to 10 (e.g. 7.5)",
                         reply_markup=keyboards.intensity_keyboard)
    else:
        db.set_step(chat_id, LogStep.FINISH_LOG)
        print_current_log(chat_id)


def process_intensity(message):
    chat_id = message.chat.id
    intensity = message.text
    try:
        intensity_val = float(intensity)
        if intensity_val < 0:
            bot.reply_to(message, "Please, indicate your pain level from 0 to 10.",
                         reply_markup=keyboards.intensity_keyboard)
            return
        if intensity_val > 10:
            bot.reply_to(message, "I am so sorry, that the pain is so strong. \nFor range consistency "
                         "reasons, please, indicate your pain level from 0 to 10.",
                         reply_markup=keyboards.intensity_keyboard)
            return

        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'intensity': intensity_val}})

        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, LogStep.LOCATION)
            bot.send_message(chat_id, f'Where the pain is located?',
                             reply_markup=keyboards.location_keyboard)
        else:
            db.set_step(chat_id, LogStep.FINISH_LOG)
            print_current_log(chat_id)

    except ValueError:
        bot.reply_to(message, "I can't interpret your answer as a numeric value. "
                     "Please, indicate your pain level from 0 to 10.", reply_markup=keyboards.intensity_keyboard)


def process_side(message):
    #try:
    chat_id = message.chat.id
    side = message.text
    if not (side.lower() in ['both', 'left', 'right']):
        bot.reply_to(message, f'Please, choose one of the listed options.')
        return

    db.log_migraine(chat_id,{'$set': {'chat_id': chat_id, 'side': side}})

    if db.get_state(chat_id) == States.LOGGING:
        db.set_step(chat_id, LogStep.ATTACK_START)
        bot.reply_to(message, 'I see. When did the pain start?', reply_markup=keyboards.pain_start_keyboard)
    else:
        db.set_step(chat_id, LogStep.FINISH_LOG)
        print_current_log(chat_id)
    #except Exception as e:
    #    bot.reply_to(message, 'Unknown error')


def process_pain_start(message):
    #try:
    chat_id = message.chat.id
    pain_start = message.text
    if not (pain_start.lower() in ['morning', 'day', 'evening', 'night']):
        bot.reply_to(message, f'Please, choose one of the listed options.')
        return

    attack_date = db.get_current_log(chat_id)['date']
    db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'pain_start': pain_start,
                                       'date': attack_date.replace(hour=attack_start_dict[pain_start.lower()])}})

    db.set_step(chat_id, LogStep.FINISH_LOG)
    print_current_log(chat_id)


def print_current_log(chat_id):
    migraine_log = db.get_current_log(chat_id)
    message = print_log(chat_id, migraine_log)
    bot.send_message(chat_id, 'Everything is set! Please check the logged data.\n' + message
                     + "\nIf you want to edit the data use the command /edit.",
                     reply_markup=keyboards.remove_keyboard)

    db.set_state(chat_id, States.INACTIVE)
    db.save_log(chat_id)

    '''markup = telebot.types.ReplyKeyboardMarkup()
    item_no = telebot.types.KeyboardButton('No')
    item_4h = telebot.types.KeyboardButton('In 4 hours')
    item_8h = telebot.types.KeyboardButton('In 8 hours')
    item_tmr = telebot.types.KeyboardButton('Tomorrow')

    markup.row(item_no, item_4h)
    markup.row(item_8h, item_tmr)

    bot.reply_to(message, 'Shall I remind you to log duration of the attack? '
                 'You can also type own number of hours', reply_markup=markup)'''

    # except Exception as e:
    #    bot.reply_to(message, 'Unknown error')


def print_log(chat_id, migraine_log):
    message = f"Date: {migraine_log['date'].strftime('%d %b %y (%A)')}.\n" \
    f"Pain intensity: {migraine_log['intensity']}.\n" \
    f"Pain location: {migraine_log['side']}." \
    f"\nPain started: {migraine_log['pain_start']}."
    return message


