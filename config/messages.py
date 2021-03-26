from config.config import terms

help_message = {'en': "Hey, I am a bot for tracking headaches and migraines! Here is the list of "
                      "the possible commands:\n/log - log an attack"
                      "\n/cancel - cancel a logging or editing"
                      "\n/edit - edit a logged attack "
                      "\n/stats - get .csv file of logged attacks "
                      "\n/calendar - get a month calendar of past attacks along"
                      " with their pain intensities"
                      "\n/language - change language (Russian, English)"
                      "\n/settings - change name or list of preferred medications"
                      "\n/help - get list of possible commands",
                'ru': "Привет, я бот для отслеживания головных болей и мигреней! Вот список возможных команд:"
                      "\n/log - внести в дневник приступ"
                      "\n/cancel - отменить логирование или редактирование "
                      "\n/edit - редактировать запись"
                      "\n/stats - получить .csv файл внесенных приступов"
                      "\n/calendar - получить месячный календарь прошлых приступов с интенсивностью боли"
                      "\n/language - поменять язык (русский, английский)"
                      "\n/settings - поменять имя или список обезболивающих"
                      "\n/help - получить список возможных команд"}

start_message = {'en': "Before we start, please, read carefully "
                       f"[terms and privacy policy]({terms}). "
                       "By continuing using this bot you agree to the terms & privacy policy.\n\n"
                       "Please, note also, this bot is currently in development. This means, that "
                       "the functionality is not full (as planned) and bugs are possible. "
                       "If you feel uncomfortable about it, please, wait until the development "
                       "is finished, "
                       "it will be stated in the about section on the bot's profile page.",
                 'ru': "Перед тем, как мы начнем, пожалуйста, прочтите внимательно "
                       f"[согласие на обработку данных]({terms}). Продолжая использовать этот бот, вы соглашаетесь "
                       "на обработку данных.\n\n"
                       "Также, обратите внимание, что бот еще в разработке. Это значит, что не все функции реализованы "
                       "(как запланировано) и ошибки возможны. Если вам некомфортно из-за возможных багов,"
                       " пожалуйста, дождитесь завершения разработки, об этом будет написано в описании бота на "
                       "странице профиля."}

ask_name_message = {'en': "Now let's know each other. What's your name?\nIf you prefer not to tell me your name "
                          "just use /cancel. ",
                    'ru': "Теперь давай познакомимся. Как вас зовут?\nЕсли вы предпочитаете не говорить мне свое "
                          "имя, просто используйте /cancel. "}

settings_name = "Now you can set your name and your preferred medications in /settings. Name is just " \
                "to know how to call you (optional), and the list of your medications will appear as buttons" \
                " for your " \
                "convenience when you log "\
                "a headache or migraine attack. \nTo change language use /language\n\n"\
                "\U0001F1F7\U0001F1FA Теперь вы можете указать в /settings свое имя и препараты," \
                " которые вы обычно принимаете. Имя"\
                " для того, чтобы знать, как к вам обращаться (опционально), а " \
                "список препаратов будет появляться " \
                "в виде кнопок для вашего удобства во "\
                "время логирования приступа головной боли или мигрени. " \
                "Чтобы поменять язык, используйте "\
                "/language (по умолчанию английский)"

delete_name = {'en': "Sure, it's your choice. I just forgot your name, my friend! ",
               'ru': "Конечно, это ваш выбор. Я просто забыл ваше имя, мой друг!"}

change_lang_name = {'en': "Sure! I changed the language. So what's your name?",
                    'ru': "Конечно! Я поменял язык. Как вас зовут?"}

error_message = {'en': "Oh no! Something went wrong! Don't worry, "
                       "I will figure it out!",
                 'ru': "О нет! Что-то пошло не так! Не волнуйтесь, я выясню, в чем проблема!"}

hint_log_message = {'en': "If you want to log an attack, just use the command "
                          "/log.",
                    'ru': "Если вы хотите залогировать приступ, используйте команду /log."}

hint_stats_message = {'en': "If you want to get statistics, just use commands /stats"
                            " to get .csv file and /calendar to get a calendar of past attacks along"
                            " with their pain intensities",
                      'ru': "Если вы хотите получить статистику, просто используйте команду /stats, "
                            "чтобы получить .csv файл и /calendar, чтобы получить календарь прошлых приступов"
                            "с их интенсивностью боли."}

hint_settings = {'en': "If you want to change name or your preferred medications, use /settings. If you want to change "
                       "language, use /language",
                 'ru': "Если вы захотите изменить имя или список предпочитаемых обезболивающих, используйте /settings. "
                       "Если вы захотите изменить язык, используйте /language"}

hint_edit = {'en': "If you want to edit an attack, just use /edit command. ",
             'ru': "Если вы захотите редактировать запись, используйте /edit. "}

nothing_cancel_message = {'en': "Nothing to cancel. " + hint_log_message['en'],
                          'ru': 'Отменять нечего. ' + hint_log_message['ru']}
cancel_log_message = {'en': "OK, I cancelled this log. " + hint_log_message['en'],
                      'ru': "ОК, я отменил логирование. " + hint_log_message['ru']}

cancel_stats_message = {'en': "OK, I cancelled this operation. " + hint_stats_message['en'],
                        'ru': "Хорошо, я отменил эту операцию. " + hint_stats_message['ru']}

cancel_settings = {'en': "Ok, quitting settings. " + hint_settings['en'],
                   'ru': "Хорошо, выхожу из настроек. " + hint_settings['ru']}

cancel_edit = {'en': "OK, I cancelled editing. " + hint_edit['en'],
               'ru': "Хорошо, я отменил редактирование " + hint_edit['ru']}

cancel_operation = {'en': "Ok, I cancelled this operation. ",
                    'ru': "Хорошо, я отменил эту операцию. "}

already_logging = {'en': "I've already started logging. If you want to cancel, just use /cancel.",
                   'ru': "Я уже начал логирование. Если вы хотите отменить, просто используйте /cancel."}

interrupt_edit = {'en': "If you want to interrupt editing and start logging or know statistics,"
                        " please, use first /cancel. ",
                  'ru': "Если вы хотите прервать редактирование и начать логирование или узнать"
                        " статистику, пожалуйста, используйте сначала /cancel. "}

start_logging = {'en': 'Hi, {name}! You started to log a headache or migraine attack.\n'
                       'Sorry to hear that! '
                       'When was the attack? \n'
                       'There is no date you need?  \U0001F914 You can '
                       'enter the date in the format dd-mm (for the current year) or dd-mm-yy (e.g. 12-08-19). ',
                 # 'You '
                 # "might type also relative date (e.g. _a week ago, yesterday, on Tuesday_), ",
                 'ru': 'Привет, {name}! Мне жаль, что у вас был приступ! Когда он был? \n'
                       'Нет подходящей даты? \U0001F914 Вы можете'
                       ' ввести дату в формате дд-мм (для текущего года) или '
                       'дд-мм-гг (например, 12-08-20) '
                 # 'или использовать относительную дату (например, _неделю назад, '
                 # 'вчера, во вторник_) '}
                 }

log_immediately_cancel = {'en': 'I canceled the previous operation and logged '
                                "this attack. I'm so sorry to know you're experiencing the pain now \U0001f614",
                          'ru': 'Я отменил предыдущую операцию и залогировал этот приступ. Мне очень жаль, что'
                                ' вы испытываете боль сейчас \U0001f614'}

log_immediately = {'en': 'I logged '
                         "this attack. I'm so sorry to know you're experiencing the pain now \U0001f614",
                   'ru': 'Я залогировал этот приступ. Мне очень жаль, что'
                         ' вы испытываете боль сейчас \U0001f614'}

already_edit = {'en': "I've already started editing. If you want to cancel or"
                      " log, use /cancel.",
                'ru': "Я уже начал редактирование. Если вы хотите отменить или "
                      "начать логирование, используйте /cancel. "}

edit_location = {'en': 'Ok, let\'s edit the location of pain. '
                       'Just choose where the pain was located. ',
                 'ru': "Хорошо, давайте отредактируем расположение очага боли. Выберите с какой стороны "
                       "болело сильнее "}

edit_intensity = {'en': 'You can now tell a correct value of the pain level from 0 to 10. ',
                  'ru': "Теперь можете указать интенсивность боли от 0 до 10. "}

edit_date = {'en': 'Please, choose now the correct option or enter the date in '
                   'the format dd-mm or dd-mm-yy',
             'ru': "Выберите, пожалуйста, теперь дату приступа из предложенных вариантов"
                   " или введите её в формате дд-мм или дд-мм-гг "}

edit_pain_start = {'en': 'Sure, just choose the correct option of the pain start',
                   'ru': "Конечно, просто выберите время начала боли "}

ask_what_edit = {'en': 'What would you like to edit?',
                 'ru': 'Что вы бы хотели отредактировать? '}

suggest_n_attack_dates = {'en': 'Please choose the date of an attack you would like to edit. Here are '
                                'dates of your most recent attacks.\n\n You can choose '
                                'one of the listed options or type the date in the format dd-mm-yy.',
                          'ru': 'Пожалуйста, выберите дату приступа, которую вы бы хотели отредактировать. Здесь'
                                ' даты ваших последних приступов.\n\n Вы можете выбрать одну из предложенных опций или'
                                ' ввести дату в формате дд-мм-гг.   '}

edit_medication = {'en': 'Sure, let\'s edit medications. Did you take any medication and if so, which ones? '
                         'Choose now a correct option or enter the name of medication. ',
                   'ru': 'Разумеется, давайте отредактируем принятое обезболивающее. Принимали ли Вы обезболивающие и'
                         ' если да, то какие? Выберите один из вариантов или введите имя препарата. '}

edit_print_log = {'en': 'Here are the details of the attack for the chosen date:\n {printed_log}'
                        '\nWhat would you like to edit?',
                  'ru': "Вот детали приступа за выбранную дату:\n {printed_log}\nЧто вы бы хотели отредактировать?"}

edit_no_attacks = {'en': 'There are no attacks for the chosen date. Please choose another date '
                         'from the listed options or enter the date in the format dd-mm-yy',
                   'ru': 'За выбранную дату не найдено приступов. Пожалуйста, выберите другую дату из предложенных '
                         'вариантов или введите дату в формате дд-мм-гг'}

edit_multiple_attacks = {'en': "For the chosen date there are multiple attacks, here are the details.\n\n"
                               "{printed_logs} Please choose the number of an attack you'd like to edit",
                         'ru': "Я нашел несколько приступов за выбранную дату, вот их детали.\n\n {printed_logs} "
                               "Пожалуйста, выберите номер приступа, который хотели бы отредактировать"}

edit_got_it = {'en': 'Got it. What would you like to edit?',
               'ru': 'Понял. Что бы вы хотели отредактировать? '}

nice_to_meet = {'en': 'Nice to meet you, {name}!',
                'ru': 'Приятно познакомиться, {name}!'}

default_name = {'en': 'my friend',
                'ru': 'мой друг'}

cancel_name = {'en': 'No problem! You can set or change your name later in /settings',
               'ru': 'Без проблем! Вы можете указать или поменять ваше имя позже в /settings '}

interrupt_log = {'en': 'If you want to interrupt logging and know e.g. statistics, use '
                       'first /cancel and then the command you need',
                 'ru': 'Если вы хотите прервать логирование и узнать, например, статистику, используйте сначала '
                       '/cancel, а затем команду, которая вам нужна '}

edit_start_log = {'en': 'In this log there is nothing to edit yet. If you want to edit another attack, use first '
                        '/cancel and then /edit. ',
                  'ru': 'В этой записи еще нечего редактировать. Если вы хотите редактировать другой приступ, '
                        'используйте сначала /cancel, а затем /edit. '}

# ASK LOG QUESTIONS

ask_intensity = {'en': "How would you estimate intensity of the pain from 0 to 10? "
                       "You might want"
                       " to use the suggested keyboard or type any numeric value"
                       " from 0 to 10 (e.g. 7.5)",
                 'ru': "Как вы оцениваете интенсивность боли от 0 до 10? Вы можете использовать предложенную "
                       "клавиатуру или ввести любое число от 0 до 10 (например, 7.5)"}

ask_location = {'en': 'Where the pain is located?',
                'ru': 'Где больше болит?'}

ask_pain_start = {'en': 'I see. When did the pain start?',
                  'ru': 'Понимаю. Когда началась боль?'}

ask_medication = {'en': 'Did you take any medication? If so, which ones? Choose one from the '
                        'listed options or enter the medication name. ',
                  'ru': 'Принимали ли вы обезболивающие? Если да, то какие? Выберите один из предложенных вариантов'
                        ' или введите название препарата. '}

ask_multiple_medication = {'en': 'Sure, choose or type medications you have taken.  ',
                           'ru': 'Конечно, просто выберите или введите принятые препараты. '}

ask_next_medication = {'en': 'Got it, anything else? \nChoose now another medication or press Done.  ',
                       'ru': 'Записал, что-то еще? \nВыберите теперь другой препарат из списка или нажмите Готово. '}

empty_meds_list = {'en': "\n\n_You don't have any "
                         "preferred medications yet. You can compose your usual"
                         " medication list in /settings. For your convenience"
                         " during logging your medications will"
                         " appear in "
                         "the keyboard below. "
                         "Alternatively, just type the name of your "
                         "medication._",
                   'ru': "\n\n_Ваш список обезболивающих, которые вы принимаете обычно,"
                         " еще пуст. Вы можете составить этот список в "
                         "/settings. Для вашего удобства во время логирования,"
                         " ваши предпочитаемые обезболивающие будут "
                         "предложены в виде кнопок. Пока что можете просто ввести имя своего обезболивающего. _"}

finish_log = {'en': "Everything is set! Please check the logged data.\n{message}"
                    " \nIf you want to edit the data use the command /edit.\nIf you want to see statistics, use "
                    "/calendar or /stats.",
              'ru': 'Готово! Пожалуйста, проверьте данные, которые я записал.\n{message}'
                    '\nЕсли вы хотите что-то отредактировать, используйте /edit.\nЕсли хотите посмотреть статистику, '
                    'используйте /calendar или /stats. '}

#  NOT A VALID ANSWER

not_int_intensity = {'en': "I can't interpret your answer as a numeric value. "
                           "Please, indicate your pain level from 0 to 10.",
                     'ru': "У меня не получается интерпретировать ваш ответ как число. Пожалуйста, введите уровень"
                           " боли от 0 до 10. "}

not_option = {'en': "Hmm... I didn't understand you. Please, choose one of the listed options.",
              'ru': 'Хмм... Я не понял вас. Пожалуйста, выберите один из предложенных вариантов. '}

neg_int = {'en': "Please, indicate your pain level from 0 to 10.",
           'ru': "Пожалуйста, укажите уровень своей боли от 0 до 10. "}

too_big_intensity = {'en': "I am so sorry, that the pain is so strong. \nFor range consistency "
                           "reasons, please, indicate your pain level from 0 to 10.",
                     'ru': "Мне очень жаль, что боль настолько сильная. \nНо все же для единообразия интенсивностей "
                           "укажите, пожалуйста, уровень своей боли от 0 до 10. "}

not_int = {'en': 'Please choose an integer number.',
           'ru': 'Пожалуйста, выберите целое число. '}

too_big_number = {'en': 'The entered number is too big or too small. '
                        '\nPlease choose the number of an attack you want to edit.',
                  'ru': 'Введенное число слишком большое или слишком маленькое. \n Пожалуйста, выберите номер'
                        'приступа, который вы бы хотели отредактировать. '}

not_name = {'en': "Before proceeding to commands, let me first know you. What's your name?",
            'ru': "Перед тем, как мы перейдем к командам, давай сначала познакомимся. Как вас зовут? "}

not_date = {'en': "I can't interpret your answer as a date. Please, enter the date"
                  " in the format dd-mm or dd-mm-yy or choose one of the listed options.",
            'ru': "Я не могу интерпретирвать ваш ответ как дату. Пожалуйста, введите дату в формате дд-мм или"
                  " дд-мм-гг или"
                  " выберите один из предложенных вариантов. "}

choose_listed = {'en': 'Please, choose one of the listed options or use /cancel to cancel'
                       'editing operation.',
                 'ru': 'Пожалуйста, выберите один из предложенных вариантов или /cancel, '
                       'чтобы отменить редактирование. '}

not_medication = {'en': "Please don't use a slash (/) in the medication name so that I don't confuse it with command. "
                        "If you want to use a command, first type /cancel to cancel current operation. ",
                  'ru': 'Пожалуйста, не используйте слеш (/) в названии препарата, чтобы я'
                        ' не перепутал это с командой. '
                        'Если вам нужно использовать команду, сначала введите /cancel, чтобы отменить текущую '
                        'операцию. '}

# PRINT LOG
log_dict = {'en': {'date': 'Date', 'intensity': 'Pain intensity', 'side': 'Pain location',
                   'pain_start': 'Pain started', 'medication': 'Medication taken'},
            'ru': {'date': 'Дата', 'intensity': 'Интенсивность боли', 'side': 'Местоположение очага боли',
                   'pain_start': 'Боль началась', 'medication': 'Было принято обезболивающее'}}

attack_start_dict = {'night': 0, 'morning': 6, 'day': 12, 'evening': 18,
                     'ночью': 0, 'утром': 6, 'днем': 12, 'вечером': 18}

# STATS
no_logs = {'en': 'There are no logs yet! If you want to log an attack, use /log',
           'ru': 'Пока еще нет ни одной записи! Если вы хотите залогировать приступ, используйте /log'}

sent_csv = {'en': 'Sure, here is your .csv file! If you want to get a month calendar'
                  ' of past attacks use /calendar.',
            'ru': 'Конечно, вот ваш .csv файл! Если вы хотите получить месячных календарь прошедших приступов, '
                  'используйте '
                  '/calendar. '}

finish_calendars = {'en': 'Ok, finishing sending calendars. Use /calendar when you want to '
                          'get a month calendar'
                          ' of attacks next time',
                    'ru': 'Хорошо, заканчиваю отправлять календари. Используйте /calendar, когда захотите получить '
                          'месячный календарь прошедших приступов в следующий раз. '}

not_month = {'en': 'Please, choose one of the listed options or '
                   'enter a month in the format mm-yy.',
             'ru': 'Пожалуйста, выберите один из предложенных вариантов или введите месяц в формате мм-гг. '}

sent_calendar = {'en': 'Sure, here you are! To continue just choose another month or '
                       'press Finish otherwise. ',
                 'ru': 'Разумеется, вот и календарь! Чтобы продолжить выберите другой месяц или нажмите Закончить. '}

sent_current_calendar = {'en': 'Hi, {name}! Here is calendar of attacks for the current month. '
                               '\nIf you want to get a calendar '
                               'for another '
                               'month, just choose this month or enter the month and year in the '
                               'format mm-yy (e.g. 08-20)',
                         'ru': 'Привет, {name}! Вот календарь приступов за текущий месяц. '
                               '\nЕсли вы хотите получить календарь за другой месяц, просто '
                               'выберите этот месяц или введите месяц и год в формате мм-гг (например, 08-20)'}

start_calendar = {'en': 'Hi, {name}! Please, choose the month of current year you want '
                        'to get a calendar of attacks for.'
                        '\nIf you want to get calendar for month of another year '
                        'enter the month and year'
                        ' in the format mm-yy (e.g. 08-20)',
                  'ru': 'Привет, {name}! Пожалуйста, выберите месяц текущего года, для которого вы хотите получить '
                        'календарь приступов.\nЕсли вы хотите получить календарь для месяца другого месяца, введите '
                        'месяц и год в формате мм-гг (например, 08-20) '}

month_names = {'en': ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                      'September', 'October', 'November', 'December'],
               'ru': ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                      'Октябрь', 'Ноябрь', 'Декабрь']}

# PREFERENCES

start_settings = {'en': "Hi! Let's personalize your experience. Do you want to change name or "
                        "edit the list of medications?",
                  'ru': "Привет! Давайте сделаем логирование еще более удобным. Вы бы хотели изменить имя или "
                        "редактировать список предпочитаемых обезболивающих? "}

change_name = {'en': "Ok, you decided to set or change the name! Just enter your name here. "
                     #"If you want to leave everything as it was, just use /cancel to quit settings."
                     #"\nIf you want me not to "
                     #"use anymore your name you told me earlier, use /delete_name",
                     "\nUse /cancel to quit settings\nand /delete_name to delete your set name",
               'ru': "Хорошо, вы решили сообщить или изменить свое имя! Просто введите свое имя здесь. "
                     #"Если вы хотите оставить все как прежде, просто используйте /cancel, чтобы выйти из настроек"
                     #"\nЕсли вы хотите, чтобы "
                     #"я больше не использовал введенное ранее вами имя, используйте /delete_name"}
                     "\nИспользуйте /cancel, чтобы выйти из настроек,\nи /delete_name,"
                     " чтобы удалить установленное имя."
               }

current_meds_list = {'en': "Here is your current list of medications: ",
                     'ru': "Вот ваш текущий список обезболивающих: "}

empty_meds_list_settings = {'en': "You don't have yet any preferred medications.",
                            'ru': 'У вас еще нет предпочитаемых обезболивающих.'}

empty_meds_finish = {'en': "Your list of preferred medications is empty!",
                     'ru': "Ваш список предпочитаемых обезболивающих пуст!"}

create_meds_list = {'en': "Now you can choose from the list medications that you usually take."
                          "I recommend you to choose 3-4 for future convenience during logging.",
                    'ru': "Теперь вы можете выбрать из списка обезболивающие, которые обычно принимаете. Я рекомендую "
                          "выбрать 3-4 для удобства во время логирования. "}

hint_type_med = {'en': "Didn't find your medication? \U0001F914 \nJust type it here, it will appear in buttons above. ",
                 'ru': "Не нашли имя своего препарата? \U0001F914 \nПросто напишите его имя здесь, "
                       "оно появится в кнопках выше. "}

keyboard_removed = {'en': "_Keyboard was removed, if you want to edit "
                          "your list of medications use /settings_ ",
                    'ru': "_Кнопки были убраны, если вы хотите редактировать ваш список обезболивающих, используйте "
                          "/settings_"}

finish_meds_list = {'en': "Good! Here is the list of medications you chose: ",
                    'ru': "Отлично! Вот получившийся список обезболивающих: "}

change_language = {'en': 'Here you can change language to Russian. So which language do you prefer?',
                   'ru': 'Здесь вы можете поменять язык на английский. Так что какой язык вы предпочтете?'}

already_language = {'en': "Good, I'm already in English!",
                    'ru': "Хорошо, что я уже на русском!"}

changed_language = {'en': "Now I'm in English! Use /help to know about all possible commands and /log to log an attack",
                    'ru': "Теперь я на русском! Используйте /help, чтобы узнать о всех возможных командах и /log, чтобы"
                          " залогировать приступ головной боли или мигрени "}

add_skip_buttons = {'en': 'Ok, I added a possibility to skip a question or all questions except for the '
                          'first question about an attack date.',
                    'ru': 'Ок, я добавил возможность пропускать вопрос или все вопросы, кроме первого '
                          'о дате приступа.'}

remove_skip_buttons = {'en': 'No problem, I removed skip buttons. Less buttons, easier to log! ',
                       'ru': 'Без проблем, я убрал кнопки для пропуска. Меньше кнопок, легче логировать! '}
