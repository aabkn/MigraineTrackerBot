from config import token, States, LogStep
import telebot
import db
import datetime
import os
import keyboards


bot = telebot.TeleBot(token, parse_mode=None)
db = db.Database()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hey, I am a bot for tracking migraines! Here is the list of "
                     "the possible commands:\n/log - log a running attack"
                     "\n/past - log an ended attack"
                     "\n/cancel - cancel a logging "
                     "\n/edit - edit a logged attack "
                     "\n/get_stats - get .csv file of logged attacks "
                     "\n/help - get list of possible commands"
                     "\nNow let's know each other. What's your name?",
                     reply_markup=keyboards.remove_keyboard)

    db.set_state(message.chat.id, States.WELCOME)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Hey, I am a bot for tracking migraines! Here is the list of "
                     "the possible commands:\n/log - log a running attack "
                     "\n/past - log an ended attack"
                     "\n/cancel - cancel a logging "
                     "\n/edit - edit a logged attack "
                     "\n/get_stats - get .csv file of logged attacks "
                     "\n/help - get list of possible commands")


@bot.message_handler(commands=['cancel'])
def cancel_log(message):
    chat_id = message.chat.id
    state = db.get_state(chat_id)
    if state in [States.INACTIVE, States.WELCOME]:
        bot.reply_to(message, "Nothing to cancel. If you want to log an attack, just use commands /log to log "
                              "a running attack or /past to log an ended attack.",
                     reply_markup=keyboards.remove_keyboard)
        return

    db.delete_current_log(chat_id)
    db.set_state(chat_id, States.INACTIVE)
    bot.reply_to(message, "OK, I cancelled this log. If you want to log an attack, just use commands /log to log "
                          "a running attack or /past to log an ended attack.",
                 reply_markup=keyboards.remove_keyboard)


@bot.message_handler(commands=['past'])
def start_log_past(message):
    chat_id = message.chat.id
    name = db.get_username(chat_id)
    if db.get_state(chat_id) == States.LOGGING:
        bot.reply_to(message, "I've already started logging. If you want to cancel, just use /cancel.")
        return
    bot.reply_to(message, f'Hi, {name}! You started a log of an ended attack '
                          f'When was the attack? You can choose one of the listed options or '
                          f'enter the date in the format dd-mm-yy',
                 reply_markup=keyboards.date_keyboard)

    db.set_step(chat_id, LogStep.DATE)
    db.set_state(chat_id, States.LOGGING)


@bot.message_handler(commands=['log'])
def start_log(message):
    chat_id = message.chat.id
    name = db.get_username(chat_id)
    if db.get_state(chat_id) == States.LOGGING:
        bot.reply_to(message, "I've already started logging. If you want to cancel, just use /cancel.")
        return
    bot.reply_to(message, f'Hi, {name}! You logged a migraine attack. \nSorry to hear that! '
                 f'How would you estimate intensity of the pain from 0 to 10? You might want to use the suggested '
                 f'keyboard or type any numeric value from 0 to 10 (e.g. 7.5)',
                 reply_markup=keyboards.intensity_keyboard)

    db.set_step(chat_id, LogStep.INTENSITY)
    db.set_state(chat_id, States.LOGGING)
    db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'date': datetime.date.today().strftime('%d/%m/%Y')}})


@bot.message_handler(commands=['get_stats'])
def get_stats(message):
    chat_id = message.chat.id
    file_name = db.save_stats_csv(chat_id)
    with open(file_name, 'rb') as csv_file:
        bot.send_document(chat_id, csv_file)
    os.remove(file_name)


@bot.message_handler(commands=['edit'])
def start_edit(message):
    chat_id = message.chat.id
    step = db.get_step(chat_id)
    if db.get_state(chat_id) == States.LOGGING:
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
        db.fetch_last_log(chat_id)
        bot.send_message(chat_id, 'What would you like to edit?',
                         reply_markup=keyboards.edit_keyboard)


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
    elif step == LogStep.FINISH_LOG:
        chosen_option = message.text
        if not(chosen_option.lower() in ['intensity', 'pain location', 'pain start', 'side', 'location',
                                         'start', 'date']):
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


@bot.message_handler(func=lambda message: db.get_step(message.chat.id) == LogStep.DATE)
def process_date(message):
    chat_id = message.chat.id
    date = message.text
    date_options = keyboards.date_options(datetime.date.today())
    if date in date_options:
        days_delta = date_options.index(date)
        attack_date = datetime.date.today() - datetime.timedelta(days=days_delta)
    else:
        try:
            attack_date = datetime.datetime.strptime(date, '%d-%m-%y')
        except ValueError:
            bot.reply_to(message, "I can't interpret your answer as a date. "
                                  "Please, enter the date in the format dd-mm-yy or choose one of the listed options.")
    db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'date': attack_date.strftime('%d/%m/%Y')}})

    if db.get_state(chat_id) == States.LOGGING:
        db.set_step(chat_id, LogStep.INTENSITY)
        bot.send_message(chat_id, "How would you estimate your pain level from 0 to 10?",
                         reply_markup=keyboards.remove_keyboard)
    else:
        db.set_step(chat_id, LogStep.FINISH_LOG)
        print_current_log(message)


@bot.message_handler(func=lambda message: db.get_step(message.chat.id) == LogStep.INTENSITY)
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
            print_current_log(message)

    except ValueError:
        bot.reply_to(message, "I can't interpret your answer as a numeric value. "
                     "Please, indicate your pain level from 0 to 10.", reply_markup=keyboards.intensity_keyboard)


@bot.message_handler(func=lambda message: db.get_step(message.chat.id) == LogStep.LOCATION)
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
        print_current_log(message)
    #except Exception as e:
    #    bot.reply_to(message, 'Unknown error')


@bot.message_handler(func=lambda message: db.get_step(message.chat.id) == LogStep.ATTACK_START)
def process_pain_start(message):
    #try:
    chat_id = message.chat.id
    pain_start = message.text
    if not (pain_start.lower() in ['morning', 'day', 'evening', 'night']):
        bot.reply_to(message, f'Please, choose one of the listed options.')
        return

    db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'pain_start': pain_start}})

    db.set_step(chat_id, LogStep.FINISH_LOG)
    print_current_log(message)


@bot.message_handler(func=lambda message: db.get_step(message.chat.id) == LogStep.FINISH_LOG)
def print_current_log(message):
    chat_id = message.chat.id
    migraine_log = db.get_log(chat_id)
    message = f"Date: {migraine_log['date']}.\n" \
              f"Pain intensity: {migraine_log['intensity']}.\n" \
              f"Pain location: {migraine_log['side']}." \
              f"\nPain started: {migraine_log['pain_start']}."
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


bot.polling()

