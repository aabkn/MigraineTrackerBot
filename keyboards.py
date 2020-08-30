import telebot


def create_keyboard(options):
    items = []
    keyboard = telebot.types.ReplyKeyboardMarkup()
    for option in options:
        items.append(telebot.types.KeyboardButton(option))
    keyboard.row(*items[:len(options) // 2])
    keyboard.row(*items[len(options) // 2:])
    return keyboard


location_keyboard = create_keyboard(options=['Both', 'Left', 'Right'])
pain_start_keyboard = create_keyboard(options=['Morning', 'Day', 'Evening', 'Night'])
edit_keyboard = create_keyboard(options=['Intensity', 'Pain location', 'Pain start'])
remove_keyboard = telebot.types.ReplyKeyboardRemove(selective=False)

