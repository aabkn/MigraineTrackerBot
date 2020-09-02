from interaction import visualisation
from migraine_bot import bot, db
from config.config import States, LogStep
import os
from config import keyboards
import calendar
import datetime


@bot.message_handler(commands=['stats'])
def get_stats(message):
    chat_id = message.chat.id
    db.set_state(chat_id, States.STATS)
    file_name = db.save_stats_csv(chat_id)
    with open(file_name, 'rb') as csv_file:
        bot.send_document(chat_id, csv_file)
    os.remove(file_name)

    db.set_state(chat_id, States.INACTIVE)


@bot.message_handler(commands=['calendar'])
def ask_calendar_month(message):
    chat_id = message.chat.id
    name = db.get_username(chat_id)
    db.set_state(chat_id, States.STATS)
    bot.send_message(chat_id, f'Hi, {name}! Please, choose the month of current year you want to get a calendar '
                              f'of attacks for.'
                              f'\nIf you want to get calendar for month of another year enter the month and year'
                              f' in the format mm-yy (e.g. 08-20)',
                     reply_markup=keyboards.month_keyboard)
    db.set_step(chat_id, LogStep.CALENDAR)


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == LogStep.CALENDAR) and
                     db.get_state(message.chat.id) == States.STATS)
def get_calendar(message):
    chat_id = message.chat.id
    if message.text == 'Finish':
        db.set_state(chat_id, States.INACTIVE)
        bot.send_message(chat_id, 'Ok, finishing sending calendars. Use /calendar when you want to get a month calendar'
                                  ' of attacks next time', reply_markup=keyboards.remove_keyboard)
        return

    if not(message.text in list(calendar.month_abbr)):
        try:
            date = datetime.datetime.strptime(message.text, '%m-%y')
            month = date.month
            year = date.year
        except ValueError:
            bot.send_message(chat_id, 'Please, choose one of the listed options or enter a month in the format mm-yy.')
            return
    else:
        month = list(calendar.month_abbr).index(message.text)
        year = datetime.datetime.today().year
    month_log = db.get_stats_month(chat_id, month=month, year=year)
    file_name = visualisation.generate_calendar(chat_id, month_log, month, year)
    with open(file_name, 'rb') as calendar_img:
        bot.send_photo(chat_id, calendar_img)
    os.remove(file_name)

