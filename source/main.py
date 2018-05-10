import os
import utils
import telebot
from templates import greeting
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot(os.environ.get('token'))
bot.skip_pending = True


@bot.message_handler(commands=['start'])
def start(message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add(KeyboardButton(text='Send location', request_location=True))
	bot.send_message(message.chat.id, greeting, reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def handle_locate(message):
	bot.send_message(message.chat.id, text=utils.by_coordinates(message.location.latitude, message.location.longitude),
    	parse_mode='Markdown')


@bot.message_handler()
def handle_address(message):
	result = utils.by_address(message.text)
	bot.send_message(message.chat.id, result, parse_mode='Markdown')


if __name__ == '__main__':
	bot.polling(none_stop=True, timeout=1000)