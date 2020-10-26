from config.config import States, Steps, n_attack_days, allowed_ids
import datetime
from config import keyboards, messages
from migraine_bot import db, bot
import logging
from interaction import log_attack
from log_config.log_helper import debug_message, info_message

logger = logging.getLogger('Server')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id, return_none=True)
        if lang is None:
            lang = message.from_user.language_code
            if lang is None:
                lang = 'en'
            db.set_lang(chat_id, lang)
        msg_to = bot.send_message(chat_id, messages.help_message[lang] + '\n\n' +
                                  messages.start_message[lang],
                                  parse_mode='Markdown')
        logger.info(info_message(message, msg_to))

        if not (db.exists_user(message.chat.id)) or db.get_username(chat_id) is None:
            db.set_state(chat_id, States.INACTIVE)
            db.set_step(chat_id, Steps.INACTIVE)

            msg = bot.send_message(chat_id, messages.ask_name_message[lang])

            logger.info(f'{chat_id}: Sent "{msg.text}"')
            bot.register_next_step_handler(msg, process_name)

        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['help'])
def send_help(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        msg_to = bot.send_message(chat_id, messages.help_message[lang])

        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['migraine'])
def migraine_now(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        state = db.get_state(chat_id)
        if state in [States.LOGGING, States.EDITING]:
            db.delete_current_log(chat_id)
        if state == States.INACTIVE:
            msg_to = bot.send_message(chat_id, messages.log_immediately[lang], reply_markup=keyboards.remove_keyboard)
        else:
            msg_to = bot.send_message(chat_id, messages.log_immediately_cancel[lang],
                                      reply_markup=keyboards.remove_keyboard)
        db.log_migraine(chat_id, {'chat_id': chat_id, 'date': datetime.datetime.now()})
        db.save_log(chat_id)
        db.set_step(chat_id, Steps.INACTIVE)
        db.set_state(chat_id, States.INACTIVE)
        logger.info(info_message(message, msg_to))
    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['cancel'])
def cancel(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        state = db.get_state(chat_id)
        logger.debug(debug_message(message))

        db.set_step(chat_id, Steps.INACTIVE)
        if state == States.INACTIVE:
            msg_to = bot.reply_to(message, messages.nothing_cancel_message[lang],
                                  reply_markup=keyboards.remove_keyboard)
            logger.info(info_message(message, msg_to))
            return

        if state == States.LOGGING:
            db.delete_current_log(chat_id)
            message_to = messages.cancel_log_message[lang]
        elif state == States.STATS:
            message_to = messages.cancel_stats_message[lang]
        elif state == States.EDITING:
            db.delete_current_log(chat_id)
            message_to = messages.cancel_edit[lang]
        elif state == States.SETTINGS:
            message_to = messages.cancel_settings[lang]
        else:
            message_to = messages.cancel_operation[lang]
            logger.warning(f'{chat_id}: Unexpected state: {state}, message: {message}')

        db.set_state(chat_id, States.INACTIVE)
        msg_to = bot.reply_to(message, message_to, reply_markup=keyboards.remove_keyboard)
        logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['log'])
def start_log(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        name = db.get_username(chat_id)
        logger.debug(debug_message(message))
        if db.get_state(chat_id) == States.LOGGING:
            msg_to = bot.reply_to(message, messages.already_logging[lang])
            logger.info(info_message(message, msg_to))
            return
        if db.get_state(chat_id) == States.EDITING:
            msg_to = bot.reply_to(message, messages.interrupt_edit[lang])
            logger.info(info_message(message, msg_to))
            return

        # date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(datetime.date.today()))
        date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(
            datetime.datetime.fromtimestamp(message.date), lang))
        if name is None or name == '':
            logger.warning(f'{chat_id}: no name in database {name}')
            name = messages.default_name[lang]
        msg_to = bot.reply_to(message, messages.start_logging[lang].replace('{name}', name),
                              reply_markup=date_keyboard)

        db.set_step(chat_id, Steps.DATE)
        db.set_state(chat_id, States.LOGGING)

        logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['edit'])
def start_edit(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        step = db.get_step(chat_id)
        state = db.get_state(chat_id)
        logger.debug(debug_message(message))
        msg_to = ''
        if (state == States.EDITING) and (message.text in ['/edit', '/log']):
            msg_to = bot.send_message(chat_id, messages.already_edit[lang])
        elif state == States.LOGGING:
            if step == Steps.DATE:
                msg_to = bot.send_message(chat_id, messages.edit_start_log[lang])
            elif step == Steps.ATTACK_START:
                msg_to = bot.send_message(chat_id, messages.edit_location[lang],
                                          reply_markup=keyboards.location_keyboard[lang])
                db.set_step(chat_id, Steps.LOCATION)
            elif step == Steps.LOCATION:
                msg_to = bot.send_message(chat_id, messages.edit_intensity[lang],
                                          reply_markup=keyboards.intensity_keyboard)
                db.set_step(chat_id, Steps.INTENSITY)
            elif step == Steps.INTENSITY:
                date_keyboard = keyboards.create_keyboard(
                    options=keyboards.date_options(datetime.datetime.fromtimestamp(message.date), lang))
                msg_to = bot.send_message(chat_id, messages.edit_date[lang],
                                          reply_markup=date_keyboard)
                db.set_step(chat_id, Steps.DATE)
            elif step == Steps.MEDICATION:
                msg_to = bot.send_message(chat_id, messages.edit_pain_start[lang],
                                          reply_markup=keyboards.pain_start_keyboard[lang])
                db.set_step(chat_id, Steps.ATTACK_START)
        elif step == Steps.FINISH_LOG:
            db.set_state(chat_id, States.EDITING)
            db.set_step(chat_id, Steps.CHOOSE_EDIT)
            db.fetch_last_log(chat_id)
            msg_to = bot.send_message(chat_id, messages.ask_what_edit[lang],
                                      reply_markup=keyboards.edit_keyboard[lang])
        else:
            past_attacks_keyboard = keyboards.create_keyboard(options=db.get_last_dates(chat_id, n_attack_days))
            msg_to = bot.send_message(chat_id, messages.suggest_n_attack_dates[lang],
                                      reply_markup=past_attacks_keyboard)
            db.set_step(chat_id, Steps.CHOOSE_ATTACK)
            db.set_state(chat_id, States.EDITING)

        if msg_to == '':
            logger.warning(f'{chat_id}: Unexpected state or step: {db.get_state(chat_id)}/{db.get_step(chat_id)},'
                           f' {message}')
            return

        logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_name(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        name = message.text
        logger.debug(debug_message(message))
        if name == '/cancel':
            if not db.exists_user(chat_id) or db.get_username(chat_id) is None:
                db.insert_user(chat_id, messages.default_name[lang])
            msg_to = bot.reply_to(message, messages.cancel_name[lang],
                                  reply_markup=keyboards.remove_keyboard)
            logger.info(info_message(message, msg_to))
            return
        if name[0] == '/':
            msg_to = bot.reply_to(message, messages.not_name[lang])
            logger.info(info_message(message, msg_to))
            bot.register_next_step_handler(msg_to, process_name)
            return

        db.insert_user(chat_id, name)

        msg_to = bot.reply_to(message, messages.nice_to_meet[lang].replace('{name}', name))
        logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.LOGGING)
def log(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        lang = db.get_lang(message.chat.id)
        step = db.get_step(message.chat.id)
        if message.text[0] == '/':
            msg_to = bot.reply_to(message, messages.interrupt_log[lang])
            logger.info(info_message(message, msg_to))
            return

        if step == Steps.DATE:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_date" function')
            log_attack.process_date(message)
        elif step == Steps.INTENSITY:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_intensity" function')
            log_attack.process_intensity(message)
        elif step == Steps.ATTACK_START:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_pain_start" function')
            log_attack.process_pain_start(message)
        elif step == Steps.LOCATION:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_side" function')
            log_attack.process_side(message)
        elif step == Steps.MEDICATION:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_medication" function')
            log_attack.process_medication(message)
        elif step == Steps.MEDICATION_MULTIPLE:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_multiple_medication" function')
            log_attack.process_multiple_medication(message)
        else:
            logger.warning(f'{message.chat.id}: Unexpected step {step}, message: {message}')
    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))
