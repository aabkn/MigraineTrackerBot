from config.config import States, Steps
from config import keyboards
from migraine_bot import db, bot
from interaction import log_attacks
import logging
from config import messages
from log_config.log_helper import debug_message, info_message

logger = logging.getLogger('Server')


@bot.message_handler(commands=['language'])
def ask_language(message):
    lang = None
    try:
        chat_id = message.chat.id
        logger.debug(debug_message(message))
        lang = db.get_lang(chat_id)
        msg_to = bot.send_message(chat_id, messages.change_language[lang], reply_markup=keyboards.language_keyboard)
        logger.info(info_message(message, msg_to))
        db.set_step(chat_id, Steps.LANGUAGE)
        db.set_state(chat_id, States.SETTINGS)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['settings'])
def show_settings(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        msg_to = bot.send_message(chat_id, messages.start_settings[lang],
                                  reply_markup=keyboards.settings_keyboard[lang])

        logger.info(info_message(message, msg_to))
        db.set_state(chat_id, States.SETTINGS)
        db.set_step(chat_id, Steps.START_MEDICATION)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == Steps.LANGUAGE) and
                                          db.get_state(message.chat.id) == States.SETTINGS)
def change_language(message):
    lang = None
    try:
        chat_id = message.chat.id
        logger.debug(debug_message(message))
        lang = db.get_lang(chat_id)
        if message.text not in ['English', 'Русский']:
            msg_to = bot.send_message(chat_id, messages.not_option)
            logger.info(info_message(message, msg_to))
            return
        elif message.text == 'English' and lang == 'ru':
            db.set_lang(chat_id, 'en')
        elif message.text == 'Русский' and lang == 'en':
            db.set_lang(chat_id, 'ru')
        else:
            msg_to = bot.send_message(chat_id, messages.already_language[lang], reply_markup=keyboards.remove_keyboard)
            logger.info(info_message(message, msg_to))
            return
        lang = db.get_lang(chat_id)
        msg_to = bot.send_message(chat_id, messages.changed_language[lang], reply_markup=keyboards.remove_keyboard)
        logger.info(info_message(message, msg_to))
        db.set_state(chat_id, States.INACTIVE)
        db.set_step(chat_id, Steps.INACTIVE)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == Steps.START_MEDICATION) and
                                          db.get_state(message.chat.id) == States.SETTINGS)
def choose_settings(message):
    lang = None
    try:
        lang = db.get_lang(message.chat.id)
        logger.debug(debug_message(message))
        if message.text.capitalize() in ['Name', 'Имя']:
            msg_to = bot.send_message(message.chat.id, messages.change_name[lang],
                                      reply_markup=keyboards.remove_keyboard)
            bot.register_next_step_handler(msg_to, log_attacks.process_name)
        elif message.text.capitalize() in ['Medications', 'Обезболивающие']:
            print_meds_list(message)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def print_meds_list(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        user_meds = db.get_meds(chat_id)

        selected_meds = dict.fromkeys(keyboards.default_meds_list[lang], 0)
        selected_meds.update(dict.fromkeys(user_meds, 1))
        if user_meds:
            msg_to = bot.send_message(chat_id, messages.current_meds_list[lang] + "\n \u2022 "
                                      + "\n \u2022 ".join(user_meds),
                                      reply_markup=keyboards.remove_keyboard)
        else:
            msg_to = bot.send_message(chat_id, messages.empty_meds_list_settings[lang],
                                      reply_markup=keyboards.remove_keyboard)

        logger.info(info_message(message, msg_to))
        logger.info(f'{chat_id}: Sent: {msg_to.text}')
        msg_to = bot.send_message(chat_id, messages.create_meds_list[lang],
                                  reply_markup=keyboards.create_med_keyboard(selected_meds, lang))
        prev_msg_id = db.get_meds_msg_id(chat_id)
        if prev_msg_id is not None:
            bot.edit_message_text(chat_id=chat_id,
                                  text=messages.create_meds_list[lang] + '\n' + messages.keyboard_removed[lang],
                                  message_id=prev_msg_id,
                                  reply_markup=None,
                                  parse_mode='Markdown')

        db.set_meds_msg_id(chat_id, msg_to.message_id)
        logger.info(f'{chat_id}: Sent: {msg_to.text}')
        db.set_step(chat_id, Steps.MEDICATION)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.callback_query_handler(func=lambda call: True)
def add_meds(call):
    lang = None
    try:
        chat_id = call.message.chat.id
        lang = db.get_lang(chat_id)
        bot.answer_callback_query(callback_query_id=call.id,
                                  show_alert=False,
                                  text='')
        user_meds = db.get_meds(chat_id)
        logger.debug(debug_message(call.message))
        if call.data == 'done':
            bot.edit_message_text(chat_id=chat_id,
                                  text=messages.create_meds_list[lang] + '\n' + messages.keyboard_removed[lang],
                                  message_id=call.message.message_id,
                                  reply_markup=None,
                                  parse_mode='Markdown')
            meds_list_str = "\n \u2022 ".join(user_meds)
            msg_to = bot.send_message(chat_id, messages.finish_meds_list[lang] + "\n \u2022 " +
                                               meds_list_str if meds_list_str else messages.empty_meds_finish[lang],
                                      reply_markup=None,
                                      parse_mode='Markdown')
            logger.info(info_message(call.message, msg_to))
            db.set_meds_msg_id(chat_id, None)
            if (db.get_state(chat_id) == States.SETTINGS) and (db.get_step(chat_id) == Steps.MEDICATION):
                db.set_state(chat_id, States.INACTIVE)
                db.set_step(chat_id, Steps.INACTIVE)
            return
        med = call.data
        selected_meds = dict.fromkeys(keyboards.default_meds_list[lang], False)
        selected_meds.update(dict.fromkeys(user_meds, True))
        logger.info(f'{chat_id}: Received call: {med}')
        logger.debug(f'{chat_id}: selected meds {selected_meds}')
        if selected_meds[med]:
            db.remove_med(chat_id, med)
        else:
            db.add_med(chat_id, med)

        selected_meds[med] = not selected_meds[med]

        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=messages.create_meds_list[lang],
                              message_id=call.message.message_id,
                              reply_markup=keyboards.create_med_keyboard(selected_meds, lang),
                              parse_mode='HTML')
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{call.message.chat.id}: {call.message.text}, {call}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(call.message, messages.error_message[lang])
        logger.info(info_message(call.message, msg_to))


@bot.message_handler(func=lambda message: (db.get_step(message.chat.id) == Steps.MEDICATION) and
                                          db.get_state(message.chat.id) == States.SETTINGS)
def add_custom_meds(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        logger.debug(debug_message(message))
        msg_id = db.get_meds_msg_id(chat_id)
        user_meds = db.get_meds(chat_id)
        selected_meds = dict.fromkeys(keyboards.default_meds_list[lang], False)
        selected_meds.update(dict.fromkeys(user_meds, True))
        med = message.text
        if med in user_meds:
            return
        selected_meds[med] = True
        db.add_med(chat_id, med)
        bot.edit_message_text(chat_id=chat_id,
                              text=messages.create_meds_list[lang],
                              message_id=msg_id,
                              reply_markup=keyboards.create_med_keyboard(selected_meds, lang),
                              parse_mode='HTML')
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))
