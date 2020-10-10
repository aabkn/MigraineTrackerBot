from config.config import token
import telebot
import database


bot = telebot.TeleBot(token, parse_mode=None)
db = database.Database()

from interaction import commands
from interaction import states