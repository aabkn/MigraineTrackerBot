import json
import logging
import logging.config
import sys

if __name__ == '__main__':
    with open('log_config/logging.json') as f:
        log_config = json.load(f)
    logging.config.dictConfig(log_config)

    from migraine_bot import bot
    bot.polling()
