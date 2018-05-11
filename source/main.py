import os
import redis
import telebot
from functools import wraps
from templates import greeting, flood_msg
from utils import by_coordinates, by_address
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot(os.environ.get('token'))


def cache(func):
	@wraps(func)
	def wrapper(message):
		r = redis.from_url(os.environ.get("REDIS_URL"))
		user = message.chat.id
		if not r.get(user):
			r.set(user, None, ex=15)
			return func(message)
		return flood_wait(user, r.ttl(user))
	return wrapper


@bot.message_handler(commands=['start'])
def start(message):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add(KeyboardButton(text='Send location', request_location=True))
	bot.send_message(message.chat.id, greeting, reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
@cache
def handle_locate(message):
	bot.send_message(message.chat.id, text=by_coordinates(message.location.latitude, message.location.longitude),
    	parse_mode='Markdown')


@bot.message_handler()
@cache
def handle_address(message):
	result = by_address(message.text)
	bot.send_message(message.chat.id, result, parse_mode='Markdown')


def flood_wait(user_id, seconds):
    bot.send_message(user_id, flood_msg.format(seconds))


if __name__ == '__main__':
	bot.skip_pending = True
	bot.polling(none_stop=True, timeout=1000)
