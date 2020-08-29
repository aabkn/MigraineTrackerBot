from config import token, States
import telebot
import db
from datetime import date
import os


bot = telebot.TeleBot(token, parse_mode=None)
db = db.Database()
remove_keyboard = telebot.types.ReplyKeyboardRemove(selective=False)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.reply_to(message, "Hey, I am a bot for tracking migraines! Here is the list of "
                                "the possible commands:\n/log: to log a running attack"
                                "\n/cancel: to cancel a logging"
                                # "\n/edit: to edit a logged attack"
                                "\n/get_stats: to get .csv file of logged attacks"
                                "\n/help: get list of possible commands"
                                "\nNow let's know each other. What's your name?", reply_markup=remove_keyboard)

    db.set_state(msg.chat.id, States.WELCOME)


@bot.message_handler(commands=['help'])
def send_help(message):
    msg = bot.reply_to(message, "Hey, I am a bot for tracking migraines! Here is the list of "
                                "the possible commands:\n/log: to log a running attack"
                                "\n/cancel: to cancel a logging"
                                # "\n/edit: to edit a logged attack"
                                "\n/get_stats: to get .csv file of logged attacks"
                                "\n/help: get list of possible commands")


@bot.message_handler(commands=['cancel'])
def cancel_log(message):
    chat_id = message.chat.id
    state = db.get_state(chat_id)
    if state in [States.NOT_LOGGING, States.WELCOME, States.FINISH_LOG]:
        bot.reply_to(message, "Nothing to cancel. If you want to log an attack, just use command /log.",
                     reply_markup=remove_keyboard)
        return

    msg = bot.reply_to(message, "OK, I cancelled this log. If you want to log an attack, just use command /log.",
                       reply_markup=remove_keyboard)
    db.set_state(msg.chat.id, States.NOT_LOGGING)


@bot.message_handler(commands=['log'])
def log(message):
    chat_id = message.chat.id
    name = db.get_username(chat_id)
    if db.get_state(chat_id) > States.START_LOG:
        bot.reply_to(message, "I've already started logging. If you want to cancel, just use /cancel.",
                     reply_markup=remove_keyboard)
        return
    bot.reply_to(message, f'Hi, {name}! You logged a migraine attack. \nSorry to hear that! '
                 f'How would you estimate intensity of the pain from 0 to 10?', reply_markup=remove_keyboard)

    db.set_state(chat_id, States.START_LOG)


@bot.message_handler(commands=['get_stats'])
def get_stats(message):
    chat_id = message.chat.id
    file_name = db.save_stats_csv(chat_id)
    with open(file_name, 'rb') as csv_file:
        bot.send_document(chat_id, csv_file)
    os.remove(file_name)


'''@bot.message_handler(commands=['edit'])
def edit(message):
    chat_id = message.chat.id
    state = db.get_state(chat_id)
    if state == States.FINISH_LOG:
        markup = telebot.types.ReplyKeyboardMarkup()
        item_intensity = telebot.types.KeyboardButton('Intensity')
        item_location = telebot.types.KeyboardButton('Pain location')
        item_start = telebot.types.KeyboardButton('Pain start')
        markup.row(item_intensity)
        markup.row(item_location, item_start)
        bot.send_message(chat_id, 'What would you like to edit?',
                         reply_markup=markup)'''


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.WELCOME)
def process_name(message):
    chat_id = message.chat.id
    name = message.text
    db.insert_user(chat_id, name)

    bot.reply_to(message, f'Nice to meet you, {name}!', reply_markup=remove_keyboard)
    db.set_state(chat_id, States.NOT_LOGGING)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.START_LOG)
def process_intensity(message):
    chat_id = message.chat.id
    intensity = message.text
    try:
        intensity_val = float(intensity)
        if intensity_val < 0:
            bot.reply_to(message, "Please, indicate your pain level from 0 to 10.", reply_markup=remove_keyboard)
            return
        if intensity_val > 10:
            bot.reply_to(message, "I am so sorry, that the pain is so strong. \nFor range consistency "
                         "reasons, please, indicate your pain level from 0 to 10.", reply_markup=remove_keyboard)
            return

        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'intensity': intensity_val}})
        markup = telebot.types.ReplyKeyboardMarkup()
        item_both = telebot.types.KeyboardButton('Both')
        item_left = telebot.types.KeyboardButton('Left')
        item_right = telebot.types.KeyboardButton('Right')
        markup.row(item_both)
        markup.row(item_left, item_right)
        bot.send_message(chat_id, f'Where the pain is located?',
                         reply_markup=markup)
        db.set_state(chat_id, States.SIDE)
    except ValueError:
        bot.reply_to(message, "I can't interpret your answer as a numeric value. "
                     "Please, indicate your pain level from 0 to 10.", reply_markup=remove_keyboard)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.SIDE)
def process_side(message):
    #try:
    chat_id = message.chat.id
    side = message.text
    if not (side.lower() in ['both', 'left', 'right']):
        bot.reply_to(message, f'Please, choose one of the listed options.')
        return

    db.log_migraine(chat_id,{'$set': {'chat_id': chat_id, 'side': side}})
    markup = telebot.types.ReplyKeyboardMarkup()
    item_morning = telebot.types.KeyboardButton('Morning')
    item_day = telebot.types.KeyboardButton('Day')
    item_evening = telebot.types.KeyboardButton('Evening')
    item_night = telebot.types.KeyboardButton('Night')

    markup.row(item_morning, item_day)
    markup.row(item_evening, item_night)
    bot.reply_to(message, 'I see. When did the pain start?', reply_markup=markup)
    db.set_state(chat_id, States.ATTACK_START)
    #except Exception as e:
    #    bot.reply_to(message, 'Unknown error')


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.ATTACK_START)
def process_pain_start(message):
    #try:
    chat_id = message.chat.id
    pain_start = message.text
    if not (pain_start.lower() in ['morning', 'day', 'evening', 'night']):
        bot.reply_to(message, f'Please, choose one of the listed options.')
        return

    db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'pain_start': pain_start,
                                       'date': date.today().strftime("%d/%m/%Y")}})

    migraine_log = db.get_log(chat_id)
    message = f"Pain intensity: {migraine_log['intensity']}.\n" \
              f"Pain location: {migraine_log['side']}." \
              f"\nPain started: {migraine_log['pain_start']}."
    bot.send_message(chat_id, 'Everything is set! Please check the logged data.\n' + message,
                     reply_markup=remove_keyboard)
    # + "\nIf you want to edit the data use the command /edit."
    db.set_state(chat_id, States.FINISH_LOG)
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

    #except Exception as e:
    #    bot.reply_to(message, 'Unknown error')


bot.polling()
