from interaction import visualisation
from migraine_bot import bot, db
from config.config import States, Steps
import os
from config import keyboards
from config import messages
import datetime
import logging
from log_config.log_helper import debug_message, info_message

logger = logging.getLogger('Server')


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == Steps.CALENDAR) and
                                           db.get_state(message.chat.id) == States.STATS)
def get_calendar(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        logger.debug(debug_message(message))
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
        file_name = visualisation.generate_calendar(chat_id, lang, month_log, month, year)
        try:
            with open(file_name, 'rb') as calendar_img:
                msg_to = bot.send_message(chat_id, messages.sent_calendar[lang])
                bot.send_photo(chat_id, calendar_img)
                logger.info(info_message(message, msg_to))
            os.remove(file_name)
        except FileNotFoundError as not_found_e:
            logger.exception(not_found_e)
            logger.warning(f'{chat_id}: File {file_name} not found, {message}')
            msg_to = bot.reply_to(message, messages.error_message[lang])
            logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))
