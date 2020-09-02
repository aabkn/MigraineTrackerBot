import telebot
import datetime
import calendar


def date_options(date):
    options = ['Today (' + date.strftime('%d %b') + ')',
               'Yesterday (' + (date - datetime.timedelta(days=1)).strftime('%d %b') + ')']
    for i in range(2, 5):
        past_date = date - datetime.timedelta(days=i)
        options.append(past_date.strftime('%A (%d %b)'))
    return options


def create_keyboard(options):
    items = []
    keyboard = telebot.types.ReplyKeyboardMarkup()
    for option in options:
        items.append(telebot.types.KeyboardButton(option))
    keyboard.row(*items[:len(options) // 2])
    keyboard.row(*items[len(options) // 2:])
    return keyboard


location_keyboard = create_keyboard(options=['Both', 'Left', 'Right'])
intensity_keyboard = create_keyboard(options=range(1, 11))
pain_start_keyboard = create_keyboard(options=['Morning', 'Day', 'Evening', 'Night'])
edit_keyboard = create_keyboard(options=['Intensity', 'Pain location', 'Pain start', 'Date'])
date_keyboard = create_keyboard(options=date_options(datetime.date.today()))
month_keyboard = create_keyboard(options=list(calendar.month_abbr)[1:])
month_keyboard.row('Finish')
remove_keyboard = telebot.types.ReplyKeyboardRemove(selective=False)

