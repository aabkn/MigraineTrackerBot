import telebot
import datetime
import calendar
import locale


def date_options(date, lang):
    if lang == 'ru':
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        options = ['Сегодня (' + date.strftime('%d %b') + ')',
                   'Вчера (' + (date - datetime.timedelta(days=1)).strftime('%d %b') + ')']
    else:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        options = ['Today (' + date.strftime('%d %b') + ')',
                   'Yesterday (' + (date - datetime.timedelta(days=1)).strftime('%d %b') + ')']
    for i in range(2, 5):
        past_date = date - datetime.timedelta(days=i)
        options.append(past_date.strftime('%A (%d %b)'))
    return options


def create_keyboard(options, rows=2):
    items = []
    if (len(options) > 6) and (rows == 'auto'):
        rows = len(options) // 4
    elif rows == 'auto':
        rows = 2

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        items.append(telebot.types.KeyboardButton(option))
    if len(options) < 3:
        keyboard.row(*items)
        return keyboard

    for r in range(rows - 1):
        keyboard.row(*items[len(options) // rows * r:len(options) // rows * (r + 1)])
    keyboard.row(*items[len(options) // rows * (rows - 1):])
    return keyboard


def create_med_keyboard(selected_meds, lang):
    meds_list = list(selected_meds.keys())
    print(meds_list)
    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(0, len(meds_list) - 1, 2):
        med_left = meds_list[i]
        value_left = selected_meds[med_left]

        med_right = meds_list[i + 1]
        value_right = selected_meds[med_right]
        markup.add(telebot.types.InlineKeyboardButton(text=u"\u2705" + med_left if value_left else med_left,
                                                      callback_data=med_left),
                   telebot.types.InlineKeyboardButton(text=u"\u2705" + med_right if value_right else med_right,
                                                      callback_data=med_right)
                   )
    if len(meds_list) % 2 == 1:
        med = meds_list[-1]
        value = selected_meds[med]
        markup.add(telebot.types.InlineKeyboardButton(text=u"\u2705" + med if value else med,
                                                      callback_data=med))
    markup.add(telebot.types.InlineKeyboardButton(text='Done!' if lang == 'en' else 'Готово!',
                                                  callback_data='done'))

    return markup


location_buttons = {'en': ['Both sides', 'Left', 'Right'],
                    'ru': ['С обеих сторон', 'Слева', 'Справа']}
location_keyboard = {'en': create_keyboard(options=location_buttons['en']),
                     'ru': create_keyboard(options=location_buttons['ru'])}

intensity_keyboard = create_keyboard(options=range(1, 11))

pain_start_buttons = {'en': ['Morning', 'Day', 'Evening', 'Night'],
                      'ru': ['Утром', 'Днем', 'Вечером', 'Ночью']}
pain_start_keyboard = {'en': create_keyboard(options=pain_start_buttons['en']),
                       'ru': create_keyboard(options=pain_start_buttons['ru'])}

edit_buttons = {'en': ['Date', 'Intensity', 'Pain location', 'Pain start', 'Medication', 'Edit another attack'],
                'ru': ['Дата', 'Интенсивность', 'Расположение боли', 'Время начала',
                       'Обезболивающее', 'Редактировать другой приступ']}
edit_keyboard = {'en': create_keyboard(options=edit_buttons['en'][:-1]),
                 'ru': create_keyboard(options=edit_buttons['ru'][:-1])}

edit_keyboard['en'].row('Edit another attack')
edit_keyboard['ru'].row('Редактировать другой приступ')

months_list = {'en': list(calendar.month_abbr)[1:],
               'ru': ['Янв', 'Февр', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Окт', 'Нояб', 'Дек']}
month_keyboard = {'en': create_keyboard(options=months_list['en']),
                  'ru': create_keyboard(options=months_list['ru'])}
month_keyboard['en'].row('Finish')
month_keyboard['ru'].row('Закончить')

language_keyboard = create_keyboard(options=['English', 'Русский'])

settings_buttons = {'en': ['Name', 'Medications'],
                    'ru': ['Имя', 'Обезболивающие']}
settings_keyboard = {'en': create_keyboard(options=settings_buttons['en']),
                     'ru': create_keyboard(options=settings_buttons['ru'])}

# TODO: remove future months or start with current month
remove_keyboard = telebot.types.ReplyKeyboardRemove(selective=False)

default_meds_list = {'en': ['Ibuprofen', 'Aspirin', 'Paracetamol', 'Diclofenac', 'Caffeine',
                    'Eletriptan (Relpax)', 'Sumatriptan',
                    'Naratriptan', 'Zolmitriptan (Zomig)'],
             'ru': ['Ибупрофен', 'Аспирин', 'Парацетамол', 'Диклофенак', 'Кофеин', 'Элетриптан (Релпакс)',
                    'Суматриптан', 'Наратриптан', 'Золмитриптан (Зомиг) ']}

meds_keyboard_row = {'en': ['No', 'Add multiple'],
                     'ru': ['Нет', 'Добавить несколько']}

meds_keyboard_multiple_row = {'en': 'Done \u2705',
                              'ru': 'Готово \u2705'}