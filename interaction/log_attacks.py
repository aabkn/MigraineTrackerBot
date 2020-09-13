from config.config import States, LogStep, attack_start_dict, n_attack_days, terms
import datetime
from config import keyboards
from migraine_bot import db, bot
import logging
from log_config.log_helper import debug_message, info_message

logger = logging.getLogger('Server')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        msg_to = bot.send_message(chat_id, "Hey, I am a bot for tracking migraines! Here is the list of "
                                           "the possible commands:\n/log - log a running attack"
                                           "\n/cancel - cancel a logging "
                                           "\n/edit - edit a logged attack "
                                           "\n/stats - get .csv file of logged attacks "
                                           "\n/calendar - get a month calendar of past attacks along "
                                           "with their intensities"
                                           "\n/help - get list of possible commands\n\n"
                                           "Before we start, please, read carefully "
                                           f"[terms and privacy policy]({terms}). "
                                           "By continuing using this bot you agree to the terms & privacy policy.\n\n"
                                           "Please, note also, this bot is currently in development. This means, that "
                                           "the functionality is not full (as planned) and bugs are possible. "
                                           "If you feel uncomfortable about it, please, wait until the development "
                                           "is finished, "
                                           "it will be stated in the about section on the bot's profile page.",
                                  parse_mode='Markdown')
        logger.info(info_message(message, msg_to))

        if not (db.exists_user(message.chat.id)):
            db.set_state(chat_id, States.INACTIVE)
            db.set_step(chat_id, LogStep.INACTIVE)

            msg = bot.send_message(chat_id, "Now let's know each other. What's your name?")

            logger.info(f'{chat_id}: Sent "{msg.text}"')
            bot.register_next_step_handler(msg, process_name)

        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['help'])
def send_help(message):
    try:
        chat_id = message.chat.id
        msg_to = bot.send_message(chat_id, "Hey, I am a bot for tracking migraines! Here is the list of "
                                           "the possible commands:\n/log - log a running attack"
                                           "\n/cancel - cancel a logging "
                                           "\n/edit - edit a logged attack "
                                           "\n/stats - get .csv file of logged attacks "
                                           "\n/calendar - get a month calendar of past attacks along"
                                           " with their intensities"
                                           "\n/help - get list of possible commands")

        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['cancel'])
def cancel_log(message):
    try:
        chat_id = message.chat.id
        state = db.get_state(chat_id)
        logger.debug(debug_message(message))

        db.set_step(chat_id, LogStep.INACTIVE)
        if state == States.INACTIVE:
            msg_to = bot.reply_to(message, "Nothing to cancel. If you want to log an attack, just use commands "
                                           "/log to log an attack.",
                                  reply_markup=keyboards.remove_keyboard)
            logger.info(info_message(message, msg_to))
            logger.debug(debug_message(message))
            return

        if state == States.LOGGING:
            db.delete_current_log(chat_id)
            message_to = "OK, I cancelled this log. If you want to log an attack, just use /log to log " \
                         "an attack."
        elif state == States.STATS:
            message_to = "OK, I cancelled this operation. If you want to get statistics, just use commands /stats" \
                         " to get .csv file and /calendar to get a calendar of past attacks along" \
                         " with their intensities"
        elif state == States.EDITING:
            db.delete_current_log(chat_id)
            message_to = "OK, I cancelled editing. If you want to edit an attack, just use /edit command. "
        else:
            message_to = "Ok, I cancelled this operation."
            logger.warning(f'{chat_id}: Unexpected state: {state}, message: {message}')

        db.set_state(chat_id, States.INACTIVE)
        msg_to = bot.reply_to(message, message_to, reply_markup=keyboards.remove_keyboard)
        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['log'])
def start_log(message):
    try:
        chat_id = message.chat.id
        name = db.get_username(chat_id)
        if db.get_state(chat_id) == States.LOGGING:
            msg_to = bot.reply_to(message, "I've already started logging. If you want to cancel, just use /cancel.")
            logger.info(info_message(message, msg_to))
            return

        date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(datetime.date.today()))
        msg_to = bot.reply_to(message, f'Hi, {name}! You started to log a migraine attack.\nSorry to hear that! '
                                       f'When was the attack? You can choose one of the listed options or '
                                       f'enter the date in the format dd-mm-yy',
                              reply_markup=date_keyboard)

        db.set_step(chat_id, LogStep.DATE)
        db.set_state(chat_id, States.LOGGING)

        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(commands=['edit'])
def start_edit(message):
    try:
        chat_id = message.chat.id
        step = db.get_step(chat_id)
        state = db.get_state(chat_id)
        logger.debug(debug_message(message))
        msg_to = ''
        if (state == States.EDITING) and (message.text == '/edit'):
            msg_to = bot.send_message(chat_id, "I've already started editing. If you want to cancel, use /cancel.")
        elif state == States.LOGGING:
            if step == LogStep.ATTACK_START:
                msg_to = bot.send_message(chat_id, 'Ok, let\'s edit the location of pain. '
                                                   'Just choose the correct option',
                                          reply_markup=keyboards.location_keyboard)
                db.set_step(chat_id, LogStep.LOCATION)
            elif step == LogStep.LOCATION:
                msg_to = bot.send_message(chat_id, 'You can now tell a correct value of the pain level from 0 to 10',
                                          reply_markup=keyboards.intensity_keyboard)
                db.set_step(chat_id, LogStep.INTENSITY)
            elif step == LogStep.INTENSITY:
                date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(datetime.date.today()))
                msg_to = bot.send_message(chat_id, 'Please, choose now the correct option or enter the date in '
                                                   'the format dd-mm-yy',
                                          reply_markup=date_keyboard)
                db.set_step(chat_id, LogStep.DATE)
        elif step == LogStep.FINISH_LOG:
            db.set_state(chat_id, States.EDITING)
            db.set_step(chat_id, LogStep.CHOOSE_EDIT)
            db.fetch_last_log(chat_id)
            msg_to = bot.send_message(chat_id, 'What would you like to edit?',
                                      reply_markup=keyboards.edit_keyboard)
        else:
            past_attacks_keyboard = keyboards.create_keyboard(options=db.get_last_dates(chat_id, n_attack_days))
            msg_to = bot.send_message(chat_id, f'Please choose the date of an attack you would like to edit. Here are '
                                               f'{n_attack_days} dates of your most recent attacks.\n\n You can choose '
                                               f'one of the listed options or type the date in the format dd-mm-yy.',
                                      reply_markup=past_attacks_keyboard)
            db.set_step(chat_id, LogStep.CHOOSE_ATTACK)
            db.set_state(chat_id, States.EDITING)

        if msg_to == '':
            logger.warning(f'{chat_id}: Unexpected state or step: {db.get_state(chat_id)}/{db.get_step(chat_id)},'
                           f' {message}')

        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.EDITING)
def edit(message):
    try:
        chat_id = message.chat.id
        step = db.get_step(chat_id)
        logger.debug(debug_message(message))
        if step == LogStep.INTENSITY:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_intensity" function')
            process_intensity(message)
            return
        elif step == LogStep.ATTACK_START:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_pain_start" function')
            process_pain_start(message)
            return
        elif step == LogStep.LOCATION:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_side" function')
            process_side(message)
            return
        elif step == LogStep.DATE:
            logger.info(f'{chat_id}: Received {message.text}. Called "process_date" function')
            process_date(message)
            return
        elif step == LogStep.CHOOSE_EDIT:
            chosen_option = message.text
            if not (chosen_option.lower() in ['intensity', 'pain location', 'pain start', 'side', 'location',
                                              'start', 'date', 'edit another attack']):
                msg_to = bot.send_message(chat_id, 'Please, choose one of the listed options')
            else:
                if chosen_option.lower() in ['intensity']:
                    msg_to = bot.send_message(chat_id, 'You can now tell a correct value of the pain level '
                                                       'from 0 to 10',
                                              reply_markup=keyboards.intensity_keyboard)
                    db.set_step(chat_id, LogStep.INTENSITY)

                elif chosen_option.lower() in ['pain location', 'side', 'location']:
                    msg_to = bot.send_message(chat_id,
                                              'Ok, let\'s edit the location of pain. Just choose the correct option',
                                              reply_markup=keyboards.location_keyboard)
                    db.set_step(chat_id, LogStep.LOCATION)
                elif chosen_option.lower() in ['start', 'pain start']:
                    msg_to = bot.send_message(chat_id,
                                              'Now you can edit the start of the attack. Please, choose the correct'
                                              ' option', reply_markup=keyboards.pain_start_keyboard)
                    db.set_step(chat_id, LogStep.ATTACK_START)
                elif chosen_option.lower() in ['date']:
                    date_keyboard = keyboards.create_keyboard(options=keyboards.date_options(datetime.date.today()))
                    msg_to = bot.send_message(chat_id, 'Please, choose now the matching option or enter the'
                                                       ' date in the format dd-mm-yy',
                                              reply_markup=date_keyboard)
                    db.set_step(chat_id, LogStep.DATE)
                else:
                    db.set_step(chat_id, LogStep.CHOOSE_ATTACK)
                    db.delete_current_log(chat_id)
                    logger.info(f'{chat_id}: Received "{message.text}". Called "start_edit" function')
                    logger.debug(debug_message(message))
                    start_edit(message)
                    return
        elif step == LogStep.CHOOSE_ATTACK:
            date_str = message.text
            if date_str in db.get_last_dates(chat_id, n_attack_days):
                date = datetime.datetime.strptime(date_str, '%d %b %Y')
            else:
                try:
                    date = datetime.datetime.strptime(date_str, '%d-%m-%y')
                except ValueError:
                    date_keyboard = keyboards.create_keyboard(options=db.get_last_dates(chat_id, n_attack_days))
                    msg_to = bot.send_message(chat_id, 'Please, choose one of the options or enter the date in '
                                                       'the format dd-mm-yy', reply_markup=date_keyboard)
                    logger.info(info_message(message, msg_to))
                    logger.debug(debug_message(message))
                    return
            logs_date = db.get_log(chat_id, date)
            if len(logs_date) == 1:
                message_to = print_log(logs_date[0])
                msg_to = bot.send_message(chat_id, 'Here are the details of the attack for the chosen date:\n' +
                                          message_to + '\nWhat would you like to edit?',
                                          reply_markup=keyboards.edit_keyboard)
                db.set_step(chat_id, LogStep.CHOOSE_EDIT)
            elif len(logs_date) == 0:
                msg_to = bot.send_message(chat_id,
                                          'There are no attacks for the chosen date. Please choose another date '
                                          'from the listed options or enter the date in the format dd-mm-yy',
                                          reply_markup=keyboards.create_keyboard(
                                              options=db.get_last_dates(chat_id, n_attack_days)))
            else:
                message_to = ''
                for i, migraine_log in enumerate(logs_date):
                    message_to += f'{i + 1}. ' + print_log(migraine_log) + '\n'
                msg_to = bot.send_message(chat_id,
                                          "For the chosen date there are multiple attacks, here are the details.\n\n" +
                                          message_to + " Please choose the number of an attack you'd like to edit",
                                          reply_markup=keyboards.create_keyboard(range(1, 1 + len(logs_date))))
                db.set_step(chat_id, LogStep.CHOOSE_ATTACK_MULTIPLE)

        elif step == LogStep.CHOOSE_ATTACK_MULTIPLE:
            try:
                attack_num = int(message.text) - 1
                if db.keep_one_log(chat_id, attack_num) == -1:
                    msg_to = bot.reply_to(message, 'The entered number is too big or too small. '
                                                   '\nPlease choose the number of an attack you want to edit.')
                else:
                    msg_to = bot.send_message(chat_id, 'Got it. What would you like to edit?',
                                              reply_markup=keyboards.edit_keyboard)
                    db.set_step(chat_id, LogStep.CHOOSE_EDIT)
            except ValueError:
                msg_to = bot.reply_to(message, 'Please choose the valid integer number.')
        else:
            msg_to = ''
            logger.warning(f'{chat_id}: Unexpected step: {step}, message: {message}')

        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


def process_name(message):
    try:
        chat_id = message.chat.id
        name = message.text
        if name[0] == '/':
            msg_to = bot.reply_to(message, "Before proceeding to commands, let me first know you. What's your name?")
            logger.info(info_message(message, msg_to))
            bot.register_next_step_handler(msg_to, process_name)
            return

        db.insert_user(chat_id, name)

        msg_to = bot.reply_to(message, f'Nice to meet you, {name}!')
        logger.info(info_message(message, msg_to))
        logger.debug(debug_message(message))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == States.LOGGING)
def log(message):
    logger.debug(debug_message(message))
    step = db.get_step(message.chat.id)
    if message.text[0] == '/':
        msg_to = bot.reply_to(message, 'If you want to interrupt logging and know e.g. statistics, use '
                                       'first /cancel and then the command you need')
        logger.info(info_message(message, msg_to))
        return

    if step == LogStep.DATE:
        logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_date" function')
        process_date(message)
    elif step == LogStep.INTENSITY:
        logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_intensity" function')
        process_intensity(message)
    elif step == LogStep.ATTACK_START:
        logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_pain_start" function')
        process_pain_start(message)
    elif step == LogStep.LOCATION:
        logger.info(f'{message.chat.id}: Received "{message.text}". Called "process_side" function')
        process_side(message)
    else:
        logger.warning(f'{message.chat.id}: Unexpected step {step}, message: {message}')


def process_date(message):
    try:
        chat_id = message.chat.id
        date = message.text
        logger.debug(debug_message(message))
        date_options = keyboards.date_options(datetime.date.today())
        print(date_options)
        if date in date_options:
            days_delta = date_options.index(date)
            attack_date = datetime.date.today() - datetime.timedelta(days=days_delta)
            attack_date = datetime.datetime(attack_date.year, attack_date.month, attack_date.day)
        else:
            try:
                attack_date = datetime.datetime.strptime(date, '%d-%m-%y')
            except ValueError:
                msg_to = bot.reply_to(message, "I can't interpret your answer as a date. Please, enter the date"
                                               " in the format dd-mm-yy or choose one of the listed options.")
                logger.info(info_message(message, msg_to))
                logger.debug(debug_message(message))
                return

        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'date': attack_date}})
        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, LogStep.INTENSITY)
            msg_to = bot.send_message(chat_id, "How would you estimate intensity of the pain from 0 to 10? "
                                               "You might want"
                                               " to use the suggested keyboard or type any numeric value"
                                               " from 0 to 10 (e.g. 7.5)", reply_markup=keyboards.intensity_keyboard)
            logger.debug(debug_message(message))
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, LogStep.FINISH_LOG)
            logger.debug(debug_message(message))
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


def process_intensity(message):
    try:
        chat_id = message.chat.id
        intensity = message.text

        logger.debug(debug_message(message))
        try:
            intensity_val = float(intensity)
            if intensity_val < 0:
                msg_to = bot.reply_to(message, "Please, indicate your pain level from 0 to 10.",
                                      reply_markup=keyboards.intensity_keyboard)
                logger.info(info_message(message, msg_to))
                return
            if intensity_val > 10:
                msg_to = bot.reply_to(message, "I am so sorry, that the pain is so strong. \nFor range consistency "
                                               "reasons, please, indicate your pain level from 0 to 10.",
                                      reply_markup=keyboards.intensity_keyboard)
                logger.info(info_message(message, msg_to))
                return

            db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'intensity': intensity_val}})

            if db.get_state(chat_id) == States.LOGGING:
                db.set_step(chat_id, LogStep.LOCATION)
                msg_to = bot.send_message(chat_id, f'Where the pain is located?',
                                          reply_markup=keyboards.location_keyboard)
                logger.info(info_message(message, msg_to))
            else:
                db.set_step(chat_id, LogStep.FINISH_LOG)
                logger.debug(debug_message(message))
                print_current_log(chat_id)

        except ValueError:
            msg_to = bot.reply_to(message, "I can't interpret your answer as a numeric value. "
                                           "Please, indicate your pain level from 0 to 10.",
                                  reply_markup=keyboards.intensity_keyboard)
            logger.info(info_message(message, msg_to))

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


def process_side(message):
    try:
        chat_id = message.chat.id
        side = message.text

        logger.debug(debug_message(message))
        if not (side.lower() in ['both', 'left', 'right']):
            msg_to = bot.reply_to(message, f'Please, choose one of the listed options.')
            logger.info(info_message(message, msg_to))
            return

        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'side': side}})

        if db.get_state(chat_id) == States.LOGGING:
            db.set_step(chat_id, LogStep.ATTACK_START)
            msg_to = bot.reply_to(message, 'I see. When did the pain start?',
                                  reply_markup=keyboards.pain_start_keyboard)
            logger.info(info_message(message, msg_to))
        else:
            db.set_step(chat_id, LogStep.FINISH_LOG)
            print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


def process_pain_start(message):
    try:
        chat_id = message.chat.id
        pain_start = message.text
        logger.debug(debug_message(message))
        if not (pain_start.lower() in ['morning', 'day', 'evening', 'night']):
            msg_to = bot.reply_to(message, f'Please, choose one of the listed options.')
            logger.info(info_message(message, msg_to))
            return

        attack_date = db.get_current_log(chat_id)['date']
        db.log_migraine(chat_id, {'$set': {'chat_id': chat_id, 'pain_start': pain_start,
                                           'date': attack_date.replace(hour=attack_start_dict[pain_start.lower()])}})

        db.set_step(chat_id, LogStep.FINISH_LOG)
        print_current_log(chat_id)

    except Exception as e:
        logger.exception(e)
        logger.critical(f'{message.chat.id}: {message.text}, {message}')
        msg_to = bot.reply_to(message, "Oh no! Something went wrong! Don't worry, "
                              "I will figure it out!")
        logger.info(info_message(message, msg_to))


def print_current_log(chat_id):
    try:
        migraine_log = db.get_current_log(chat_id)
        message = print_log(migraine_log)
        msg_to = bot.send_message(chat_id, 'Everything is set! Please check the logged data.\n' + message
                                  + "\nIf you want to edit the data use the command /edit.",
                                  reply_markup=keyboards.remove_keyboard)
        logger.info(f'{chat_id}: Sent {msg_to.text}')
        db.set_state(chat_id, States.INACTIVE)
        db.save_log(chat_id)
    except Exception as e:
        logger.exception(e)
        logger.critical(f'{chat_id}')
        raise e


def print_log(migraine_log):
    message = f"Date: {migraine_log['date'].strftime('%d %b %y (%A)')}.\n" \
              f"Pain intensity: {migraine_log['intensity']}.\n" \
              f"Pain location: {migraine_log['side']}." \
              f"\nPain started: {migraine_log['pain_start']}."
    return message
