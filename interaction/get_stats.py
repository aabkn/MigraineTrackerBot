from interaction import visualisation
from migraine_bot import bot, db
from config.config import States, Steps
import os
from config import keyboards
import calendar
from config import messages
import datetime
import logging
from log_config.log_helper import debug_message, info_message

logger = logging.getLogger('Server')


@bot.message_handler(commands=['stats'])
def get_stats(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        db.set_state(chat_id, States.STATS)
        file_name = db.save_stats_csv(chat_id)
        if file_name is None:
            msg_to = bot.send_message(chat_id, messages.no_logs[lang])
            logger.info(info_message(message, msg_to))
            return
        try:
            with open(file_name, 'rb') as csv_file:
                msg_to = bot.send_message(chat_id, messages.sent_csv[lang],
                                          reply_markup=keyboards.remove_keyboard)
                bot.send_document(chat_id, csv_file)
                logger.info(f'{chat_id}: Received: "{message.text}". Sent {msg_to.text} and document "{file_name}"')
            os.remove(file_name)
        except FileNotFoundError as not_found_e:
            logger.exception(not_found_e)
            logger.warning(f'{chat_id}: File {file_name} not found, {message}')

        db.set_state(chat_id, States.INACTIVE)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['calendar'])
def ask_calendar_month(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        name = db.get_username(chat_id)
        db.set_state(chat_id, States.STATS)
        msg_to = bot.send_message(chat_id, messages.start_calendar[lang].replace('{name}', name),
                                  reply_markup=keyboards.month_keyboard[lang])
        logger.info(info_message(message, msg_to))
        db.set_step(chat_id, Steps.CALENDAR)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == Steps.CALENDAR) and
                                          db.get_state(message.chat.id) == States.STATS)
def get_calendar(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        if message.text in ['Finish', 'Закончить']:
            db.set_state(chat_id, States.INACTIVE)
            msg_to = bot.send_message(chat_id, messages.finish_calendars[lang], reply_markup=keyboards.remove_keyboard)
            logger.info(info_message(message, msg_to))
            return

        if not (message.text in keyboards.months_list[lang]):
            try:
                date = datetime.datetime.strptime(message.text, '%m-%y')
                month = date.month
                year = date.year
            except ValueError:
                msg_to = bot.send_message(chat_id, messages.not_month[lang])
                logger.info(info_message(message, msg_to))
                return
        else:
            month = keyboards.months_list[lang].index(message.text) + 1
            year = datetime.datetime.today().year
        month_log = db.get_stats_month(chat_id, month=month, year=year)
        file_name = visualisation.generate_calendar(chat_id, month_log, month, year)
        try:
            with open(file_name, 'rb') as calendar_img:
                msg_to = bot.send_message(chat_id, messages.sent_calendar[lang])
                bot.send_photo(chat_id, calendar_img)
                logger.info(info_message(message, msg_to))
            os.remove(file_name)
        except FileNotFoundError as not_found_e:
            logger.exception(not_found_e)
            logger.warning(f'{chat_id}: File {file_name} not found, {message}')

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))
