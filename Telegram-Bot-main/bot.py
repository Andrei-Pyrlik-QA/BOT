#библиотеки, которые загружаем из вне
import telebot
TOKEN = '7197882427:AAFehyNFQ3REK7m9MefHk1RA-QYBasKarsI'

from telebot import types

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):

	#клавиатура
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton("🧡 Мой репозиторий")
	item2 = types.KeyboardButton("😋 Написать Папе")
	item3 = types.KeyboardButton("😋 Передать привет папе")

	markup.add(item1, item2)

	bot.send_message(message.chat.id, "Привет тебе от краба, {0.first_name}!".format(message.from_user, bot.get_me()),
		parse_mode='html', reply_markup=markup)

#назначаем действие для клавиатуры
@bot.message_handler(content_types=['text'])
def lalala(message):
	if message.chat.type == 'private':
		if message.text == '🧡 Мой репозиторий':
			bot.send_message(message.chat.id, 'https://github.com/AndreyRyadnovQA')
		elif message.text == '😋 Написать мне в личку':
			bot.send_message(message.chat.id, 'https://t.me/And_reyyyyy')
		else:
			bot.send_message(message.chat.id, 'Не знаю что ответить😢')
			elif message.text == '😋 Написать мне в личку':


bot.polling(none_stop=True)









#https://core.telegram.org/bots/api#available-methods
