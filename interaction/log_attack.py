from config.config import States, Steps, n_attack_days
import datetime
from config import keyboards, messages
from config.messages import attack_start_dict
from migraine_bot import db, bot
import logging
import locale
import dateparser
from log_config.log_helper import debug_message, info_message
from dateutil.relativedelta import relativedelta

logger = logging.getLogger('Server')


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
            attack_date = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})

            if (attack_date.month > datetime.date.today().month) & (attack_date.year == datetime.date.today().year):
                attack_date -= relativedelta(years=1)

            # datetime.datetime.strptime(date, '%d-%m-%y')
            if attack_date is None:
                msg_to = bot.reply_to(message, messages.not_date[lang],
                                      reply_markup=keyboards.create_keyboard(date_options))
                logger.info(info_message(message, msg_to))
                return

        db.log_migraine(chat_id, {'chat_id': chat_id, 'date': attack_date})
        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, Steps.INTENSITY)
            skip = db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING)
            msg_to = bot.send_message(chat_id, messages.ask_intensity[lang],
                                      reply_markup=keyboards.intensity_keyboard[lang][skip])
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, Steps.FINISH_LOG)
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
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
            if intensity not in keyboards.skip_row[lang]:  # SKIP or SKIP ALL
                intensity_val = float(intensity)
                if (intensity_val < 0) or (intensity_val > 10):
                    skip = db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING)
                    if intensity_val < 0:
                        msg_to = bot.reply_to(message, messages.neg_int[lang],
                                              reply_markup=keyboards.intensity_keyboard[lang][skip])
                    else:
                        msg_to = bot.reply_to(message, messages.too_big_intensity[lang],
                                              reply_markup=keyboards.intensity_keyboard[lang][skip])
                    logger.info(info_message(message, msg_to))
                    return

                db.log_migraine(chat_id, {'chat_id': chat_id, 'intensity': intensity_val})

            if intensity != keyboards.skip_row[lang][1]:

                if db.get_state(chat_id) == States.LOGGING:
                    db.set_step(chat_id, Steps.LOCATION)
                    skip = db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING)
                    msg_to = bot.send_message(chat_id, messages.ask_location[lang],
                                              reply_markup=keyboards.location_keyboard[lang][skip])
                    logger.info(info_message(message, msg_to))
                else:  # EDIT
                    db.set_step(chat_id, Steps.FINISH_LOG)
                    print_current_log(chat_id)
            else:  # SKIP ALL
                db.set_step(chat_id, Steps.FINISH_LOG)
                print_current_log(chat_id)

        except ValueError:
            skip = db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING)
            msg_to = bot.reply_to(message, messages.not_int_intensity[lang],
                                  reply_markup=keyboards.intensity_keyboard[lang][skip])
            logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
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
        if not (side.capitalize() in keyboards.location_buttons[lang] + keyboards.skip_row[lang]):
            msg_to = bot.reply_to(message, messages.not_option[lang])
            logger.info(info_message(message, msg_to))
            return

        if side not in keyboards.skip_row[lang]:
            db.log_migraine(chat_id, {'chat_id': chat_id, 'side': side})

        if (db.get_state(chat_id) == States.LOGGING) and (side != keyboards.skip_row[lang][1]):  # not(EDIT or SKIP ALL)
            db.set_step(chat_id, Steps.ATTACK_START)
            skip = db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING)
            msg_to = bot.reply_to(message, messages.ask_pain_start[lang],
                                  reply_markup=keyboards.pain_start_keyboard[lang][skip])
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, Steps.FINISH_LOG)
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
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
        if not (pain_start.capitalize() in keyboards.pain_start_buttons[lang] + keyboards.skip_row[lang]):
            msg_to = bot.reply_to(message, messages.not_option[lang])
            logger.info(info_message(message, msg_to))
            return

        if pain_start not in keyboards.skip_row[lang]:
            attack_date = db.get_current_log(chat_id)['date']
            db.log_migraine(chat_id, {'chat_id': chat_id, 'pain_start': pain_start,
                                      'date': attack_date.replace(hour=attack_start_dict[pain_start.lower()])})

        if (db.get_state(chat_id) == States.LOGGING) and (pain_start != keyboards.skip_row[lang][1]):
            db.set_step(chat_id, Steps.MEDICATION)
            user_meds = db.get_meds(chat_id)
            meds_keyboard = keyboards.create_keyboard(user_meds)
            meds_keyboard.row(*keyboards.meds_keyboard_row[lang])
            if db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING):
                meds_keyboard.row(keyboards.skip_row[lang][0])  # last question
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
        logger.error(f'{message.chat.id}: {message.text}, {message}')
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
        if message.text == keyboards.meds_keyboard_row[lang][1]:  # ADD MULTIPLE
            user_meds = db.get_meds(chat_id)
            meds_keyboard = keyboards.create_keyboard(user_meds)
            msg_to = bot.send_message(chat_id, messages.ask_multiple_medication[lang], reply_markup=meds_keyboard)
            logger.info(info_message(message, msg_to))
            db.log_migraine(chat_id, {'medication': ""})
            db.set_step(chat_id, Steps.MEDICATION_MULTIPLE)
            return
        if message.text != keyboards.skip_row[lang][0]:
            db.log_migraine(chat_id, {'chat_id': chat_id, 'medication': message.text})
        db.set_step(chat_id, Steps.FINISH_LOG)
        print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))


def process_multiple_medication(message):
    lang = None
    try:
        logger.debug(debug_message(message))
        chat_id = message.chat.id
        lang = db.get_lang(chat_id)
        if message.text[0] == '/':
            msg_to = bot.reply_to(message, messages.not_medication[lang])
            logger.info(info_message(message, msg_to))
            return

        if message.text in keyboards.meds_keyboard_multiple_row[lang]:  # DONE
            db.set_step(chat_id, Steps.FINISH_LOG)
            print_current_log(chat_id)
        else:
            # db.log_migraine(chat_id, {"$addToSet": {'medication': message.text}})
            db.log_migraine(chat_id, {'medication': message.text}, append=True)
            user_meds = db.get_meds(chat_id)
            meds_keyboard = keyboards.create_keyboard(user_meds)
            meds_keyboard.row(keyboards.meds_keyboard_multiple_row[lang])
            if db.get_skip_preference(chat_id) and (db.get_state(chat_id) == States.LOGGING):
                meds_keyboard.row(*keyboards.skip_row[lang])
            msg_to = bot.send_message(chat_id, messages.ask_next_medication[lang],
                                      reply_markup=meds_keyboard)
            logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.error(f'{message.chat.id}: {message.text}, {message}')
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
        logger.error(f'{chat_id}')
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
        # elif type(migraine_log[col]) == list:
        #    message += f"{messages.log_dict[lang][col]}: {', '.join(migraine_log[col])}.\n"
        else:
            message += f"{messages.log_dict[lang][col]}: {migraine_log[col]}.\n"

    return message
