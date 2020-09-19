from config.config import States, Steps, n_attack_days
import datetime
from config import keyboards, messages
from config.messages import attack_start_dict
from migraine_bot import db, bot
import logging
import locale
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
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
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
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['cancel'])
def cancel_log(message):
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
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
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
        msg_to = bot.reply_to(message, messages.start_logging[lang].replace('{name}', name),
                              reply_markup=date_keyboard)

        db.set_step(chat_id, Steps.DATE)
        db.set_state(chat_id, States.LOGGING)

        logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
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
            if step == Steps.ATTACK_START:
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
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.EDITING)
def edit(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        step = db.get_step(chat_id)
        logger.debug(debug_message(message))
        if step == Steps.INTENSITY:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_intensity" function')
            process_intensity(message)
            return
        elif step == Steps.ATTACK_START:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_pain_start" function')
            process_pain_start(message)
            return
        elif step == Steps.LOCATION:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_side" function')
            process_side(message)
            return
        elif step == Steps.DATE:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_date" function')
            process_date(message)
            return
        elif step == Steps.MEDICATION:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_medication" function')
            process_medication(message)
            return
        elif step == Steps.CHOOSE_EDIT:
            chosen_option = message.text
            if not (chosen_option.capitalize() in keyboards.edit_buttons[lang]):
                msg_to = bot.send_message(chat_id, messages.choose_listed[lang])
            else:
                if chosen_option.lower() in ['intensity', 'интенсивность']:
                    msg_to = bot.send_message(chat_id, messages.edit_intensity[lang],
                                              reply_markup=keyboards.intensity_keyboard)
                    db.set_step(chat_id, Steps.INTENSITY)

                elif chosen_option.lower() in ['pain location', 'расположение боли']:
                    msg_to = bot.send_message(chat_id,
                                              messages.edit_location[lang],
                                              reply_markup=keyboards.location_keyboard[lang])
                    db.set_step(chat_id, Steps.LOCATION)
                elif chosen_option.lower() in ['pain start', 'время начала']:
                    msg_to = bot.send_message(chat_id,
                                              messages.edit_pain_start[lang],
                                              reply_markup=keyboards.pain_start_keyboard[lang])
                    db.set_step(chat_id, Steps.ATTACK_START)
                elif chosen_option.lower() in ['date', 'дата']:
                    date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(datetime.date.today(),
                                                                                             lang))
                    msg_to = bot.send_message(chat_id, messages.edit_date[lang],
                                              reply_markup=date_keyboard)
                    db.set_step(chat_id, Steps.DATE)
                elif chosen_option.lower() in ['medication', 'обезболивающее']:
                    med_keyboard = keyboards.create_keyboard(db.get_meds(chat_id), rows='auto')
                    med_keyboard.row('No' if lang == 'en' else 'Нет')
                    msg_to = bot.send_message(chat_id, messages.edit_medication[lang],
                                              reply_markup=med_keyboard)
                    db.set_step(chat_id, Steps.MEDICATION)
                else:
                    db.set_step(chat_id, Steps.CHOOSE_ATTACK)
                    db.delete_current_log(chat_id)
                    logger.info(f'{chat_id}: Received "{message.text}". Called "start_edit" function')
                    start_edit(message)
                    return
        elif step == Steps.CHOOSE_ATTACK:
            date_str = message.text
            if date_str in db.get_last_dates(chat_id, n_attack_days):
                date = datetime.datetime.strptime(date_str, '%d %b %Y')
            else:
                try:
                    date = datetime.datetime.strptime(date_str, '%d-%m-%y')
                except ValueError:
                    date_keyboard = keyboards.create_keyboard(options=db.get_last_dates(chat_id, n_attack_days))
                    msg_to = bot.send_message(chat_id, messages.not_date[lang], reply_markup=date_keyboard)
                    logger.info(info_message(message, msg_to))
                    return
            logs_date = db.get_log(chat_id, date)
            if len(logs_date) == 1:
                printed_log = print_log(logs_date[0], lang)
                msg_to = bot.send_message(chat_id, messages.edit_print_log[lang].replace('{printed_log}', printed_log),
                                          reply_markup=keyboards.edit_keyboard[lang])
                db.set_step(chat_id, Steps.CHOOSE_EDIT)
            elif len(logs_date) == 0:
                msg_to = bot.send_message(chat_id,
                                          messages.edit_no_attacks[lang],
                                          reply_markup=keyboards.create_keyboard(
                                              options=db.get_last_dates(chat_id, n_attack_days)))
            else:
                printed_logs = ''
                for i, migraine_log in enumerate(logs_date):
                    printed_logs += f'{i + 1}. ' + print_log(migraine_log, lang) + '\n'
                msg_to = bot.send_message(chat_id,
                                          messages.edit_multiple_attacks[lang].replace('{printed_logs}', printed_logs),
                                          reply_markup=keyboards.create_keyboard(range(1, 1 + len(logs_date))))
                db.set_step(chat_id, Steps.CHOOSE_ATTACK_MULTIPLE)

        elif step == Steps.CHOOSE_ATTACK_MULTIPLE:
            try:
                attack_num = int(message.text) - 1
                if db.keep_one_log(chat_id, attack_num) == -1:
                    msg_to = bot.reply_to(message, messages.too_big_number[lang])
                else:
                    msg_to = bot.send_message(chat_id, messages.edit_got_it[lang],
                                              reply_markup=keyboards.edit_keyboard[lang])
                    db.set_step(chat_id, Steps.CHOOSE_EDIT)
            except ValueError:
                msg_to = bot.reply_to(message, messages.not_int[lang])
        else:
            msg_to = ''
            logger.warning(f'{chat_id}: Unexpected step: {step}, message: {message}')

        logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
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
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
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
            process_date(message)
        elif step == Steps.INTENSITY:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_intensity" function')
            process_intensity(message)
        elif step == Steps.ATTACK_START:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_pain_start" function')
            process_pain_start(message)
        elif step == Steps.LOCATION:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_side" function')
            process_side(message)
        elif step == Steps.MEDICATION:
            logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_medication" function')
            process_medication(message)
        else:
            logger.warning(f'{message.chat.id}: Unexpected step {step}, message: {message}')
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_date(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        date = message.text
        logger.debug(debug_message(message))
        date_options = keyboards.date_options(datetime.date.today(), lang)
        if date in date_options:
            days_delta = date_options.index(date)
            attack_date = datetime.date.today() - datetime.timedelta(days=days_delta)
            attack_date = datetime.datetime(attack_date.year, attack_date.month, attack_date.day)
        else:
            try:
                attack_date = datetime.datetime.strptime(date, '%d-%m-%y')
            except ValueError:
                msg_to = bot.reply_to(message, messages.not_date[lang],
                                      reply_markup=keyboards.create_keyboard(date_options))
                logger.info(info_message(message, msg_to))
                return

        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'date': attack_date}})
        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, Steps.INTENSITY)
            msg_to = bot.send_message(chat_id, messages.ask_intensity[lang], reply_markup=keyboards.intensity_keyboard)
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, Steps.FINISH_LOG)
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_intensity(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        intensity = message.text

        logger.debug(debug_message(message))
        try:
            intensity_val = float(intensity)
            if intensity_val < 0:
                msg_to = bot.reply_to(message, messages.neg_int[lang],
                                      reply_markup=keyboards.intensity_keyboard)
                logger.info(info_message(message, msg_to))
                return
            if intensity_val > 10:
                msg_to = bot.reply_to(message, messages.too_big_intensity[lang],
                                      reply_markup=keyboards.intensity_keyboard)
                logger.info(info_message(message, msg_to))
                return

            db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'intensity': intensity_val}})

            if db.get_state(chat_id) == States.LOGGING:
                db.set_step(chat_id, Steps.LOCATION)
                msg_to = bot.send_message(chat_id, messages.ask_location[lang],
                                          reply_markup=keyboards.location_keyboard[lang])
                logger.info(info_message(message, msg_to))
            else:
                db.set_step(chat_id, Steps.FINISH_LOG)
                print_current_log(chat_id)

        except ValueError:
            msg_to = bot.reply_to(message, messages.not_int_intensity[lang],
                                  reply_markup=keyboards.intensity_keyboard)
            logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_side(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        side = message.text

        logger.debug(debug_message(message))
        if not (side.capitalize() in keyboards.location_buttons[lang]):
            msg_to = bot.reply_to(message, messages.not_option[lang])
            logger.info(info_message(message, msg_to))
            return

        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'side': side}})

        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, Steps.ATTACK_START)
            msg_to = bot.reply_to(message, messages.ask_pain_start[lang],
                                  reply_markup=keyboards.pain_start_keyboard[lang])
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, Steps.FINISH_LOG)
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_pain_start(message):
    lang = None
    try:
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        pain_start = message.text
        logger.debug(debug_message(message))
        if not (pain_start.capitalize() in keyboards.pain_start_buttons[lang]):
            msg_to = bot.reply_to(message, messages.not_option[lang])
            logger.info(info_message(message, msg_to))
            return

        attack_date = db.get_current_log(chat_id)['date']
        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'pain_start': pain_start,
                                           'date': attack_date.replace(hour=attack_start_dict[pain_start.lower()])}})

        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, Steps.MEDICATION)
            user_meds = db.get_meds(chat_id)
            meds_keyboard = keyboards.create_keyboard(user_meds)

            meds_keyboard.row('No' if lang == 'en' else 'Нет')
            msg_to = bot.send_message(chat_id, messages.ask_medication[lang] +
                                      ('' if user_meds else messages.empty_meds_list[lang]),
                                      reply_markup=meds_keyboard,
                                      parse_mode='Markdown')
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, Steps.FINISH_LOG)
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_medication(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id

        lang = db.get_lang(chat_id)
        if message.text[0] == '/':
            msg_to = bot.reply_to(message, messages.not_medication[lang])
            logger.info(info_message(message, msg_to))
            return
        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'medication': message.text}})
        db.set_step(chat_id, Steps.FINISH_LOG)
        print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def print_current_log(chat_id):
    try:
        migraine_log = db.get_current_log(chat_id)
        lang = db.get_lang(chat_id)
        message = print_log(migraine_log, lang)
        msg_to = bot.send_message(chat_id, messages.finish_log[lang].replace('{message}', message),
                                  reply_markup=keyboards.remove_keyboard)
        logger.info(f'{chat_id}: Sent {msg_to.text}')
        db.set_state(chat_id, States.INACTIVE)
        db.save_log(chat_id)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{chat_id}')
        raise e


def print_log(migraine_log, lang='en'):
    message = ''
    for col in migraine_log.keys():
        if col not in messages.log_dict[lang].keys():
            continue
        if type(migraine_log[col]) == datetime.datetime:
            if lang == 'en':
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            elif lang == 'ru':
                locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
            message += f"{messages.log_dict[lang][col]}: {migraine_log[col].strftime('%d %b %y (%A)')}.\n"
        else:
            message += f"{messages.log_dict[lang][col]}: {migraine_log[col]}.\n"

    return message
