from config.config import States, Steps, n_attack_days
import datetime
from config import keyboards, messages
from migraine_bot import db, bot
import logging
from log_config.log_helper import debug_message, info_message
from interaction.commands.log_handler import start_edit
from interaction import log_attack

logger = logging.getLogger('Server')


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
            log_attack.process_intensity(message)
            return
        elif step == Steps.ATTACK_START:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_pain_start" function')
            log_attack.process_pain_start(message)
            return
        elif step == Steps.LOCATION:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_side" function')
            log_attack.process_side(message)
            return
        elif step == Steps.DATE:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_date" function')
            log_attack.process_date(message)
            return
        elif step == Steps.MEDICATION:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_medication" function')
            log_attack.process_medication(message)
            return
        elif step == Steps.MEDICATION_MULTIPLE:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_multiple_medication" function')
            log_attack.process_multiple_medication(message)
            return
        elif step == Steps.CHOOSE_EDIT:
            chosen_option = message.text
            if not (chosen_option.capitalize() in keyboards.edit_buttons[lang]):
                msg_to = bot.send_message(chat_id, messages.choose_listed[lang])
            else:
                if chosen_option.lower() in ['intensity', 'интенсивность']:
                    msg_to = bot.send_message(chat_id, messages.edit_intensity[lang],
                                              reply_markup=keyboards.intensity_keyboard[lang][False])
                    db.set_step(chat_id, Steps.INTENSITY)

                elif chosen_option.lower() in ['pain location', 'расположение боли']:
                    msg_to = bot.send_message(chat_id,
                                              messages.edit_location[lang],
                                              reply_markup=keyboards.location_keyboard[lang][False])
                    db.set_step(chat_id, Steps.LOCATION)
                elif chosen_option.lower() in ['pain start', 'время начала']:
                    msg_to = bot.send_message(chat_id,
                                              messages.edit_pain_start[lang],
                                              reply_markup=keyboards.pain_start_keyboard[lang][False])
                    db.set_step(chat_id, Steps.ATTACK_START)
                elif chosen_option.lower() in ['date', 'дата']:
                    date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(datetime.date.today(),
                                                                                             lang))
                    msg_to = bot.send_message(chat_id, messages.edit_date[lang],
                                              reply_markup=date_keyboard)
                    db.set_step(chat_id, Steps.DATE)
                elif chosen_option.lower() in ['medication', 'обезболивающее']:
                    med_keyboard = keyboards.create_keyboard(db.get_meds(chat_id), rows='auto')
                    med_keyboard.row(*keyboards.meds_keyboard_row[lang])
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
                printed_log = log_attack.print_log(logs_date[0], lang)
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
                    printed_logs += f'{i + 1}. ' + log_attack.print_log(migraine_log, lang) + '\n'
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
        logger.error(f'{message.chat.id}: {message.text}, {message}')
        if lang is None:
            lang = 'en'
        msg_to = bot.reply_to(message, messages.error_message[lang])
        logger.info(info_message(message, msg_to))

