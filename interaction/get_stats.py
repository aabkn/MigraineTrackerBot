from interaction import visualisation
from migraine_bot import bot, db
from config.config import States, LogStep
import os
from config import keyboards
import calendar
import datetime
import logging
from log_config.log_helper import debug_message, info_message

logger = logging.getLogger('Server')


@bot.message_handler(commands=['stats'])
def get_stats(message):
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        db.set_state(chat_id, States.STATS)
        logger.debug(debug_message(message))
        file_name = db.save_stats_csv(chat_id)
        if file_name is None:
            msg_to = bot.send_message(chat_id, 'There are no logs yet! If you want to log an attack, use /log')
            logger.info(info_message(message, msg_to))
            return
        try:
            with open(file_name, 'rb') as csv_file:
                bot.send_document(chat_id, csv_file)
                logger.info(f'{chat_id}: Received: "{message.text}". Send document "{file_name}"')
            os.remove(file_name)
        except FileNotFoundError as not_found_e:
            logger.exception(not_found_e)
            logger.warning(f'{chat_id}: File {file_name} not found, {message}')

        db.set_state(chat_id, States.INACTIVE)
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['calendar'])
def ask_calendar_month(message):
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        name = db.get_username(chat_id)
        db.set_state(chat_id, States.STATS)
        logger.debug(debug_message(message))
        msg_to = bot.send_message(chat_id, f'Hi, {name}! Please, choose the month of current year you want '
                                           f'to get a calendar of attacks for.'
                                           f'\nIf you want to get calendar for month of another year '
                                           f'enter the month and year'
                                           f' in the format mm-yy (e.g. 08-20)',
                                  reply_markup=keyboards.month_keyboard)
        logger.info(info_message(message, msg_to))
        db.set_step(chat_id, LogStep.CALENDAR)
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == LogStep.CALENDAR) and
                                           db.get_state(message.chat.id) == States.STATS)
def get_calendar(message):
    try:
        chat_id = message.chat.id
        if message.text == 'Finish':
            db.set_state(chat_id, States.INACTIVE)
            msg_to = bot.send_message(chat_id, 'Ok, finishing sending calendars. Use /calendar when you want to '
                                      'get a month calendar'
                                      ' of attacks next time', reply_markup=keyboards.remove_keyboard)
            logger.info(info_message(message, msg_to))
            return

        if not (message.text in list(calendar.month_abbr)):
            try:
                date = datetime.datetime.strptime(message.text, '%m-%y')
                month = date.month
                year = date.year
            except ValueError:
                msg_to = bot.send_message(chat_id, 'Please, choose one of the listed options or '
                                          'enter a month in the format mm-yy.')
                logger.info(info_message(message, msg_to))
                return
        else:
            month = list(calendar.month_abbr).index(message.text)
            year = datetime.datetime.today().year
        month_log = db.get_stats_month(chat_id, month=month, year=year)
        file_name = visualisation.generate_calendar(chat_id, month_log, month, year)
        try:
            with open(file_name, 'rb') as calendar_img:
                bot.send_photo(chat_id, calendar_img)
            os.remove(file_name)
        except FileNotFoundError as not_found_e:
            logger.exception(not_found_e)
            logger.warning(f'{chat_id}: File {file_name} not found, {message}')

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))
