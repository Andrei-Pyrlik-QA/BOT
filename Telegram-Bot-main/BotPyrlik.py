import telebot
from telebot import types
import random

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)

# Состояния пользователей
waiting_for_name = {}
waiting_for_greeting_response = {}
waiting_for_animal_answer = {}
waiting_for_specific_animal = {}
waiting_for_animal_name = {}
# Новые состояния для разговора об играх
waiting_for_user_favorite_game = {}  # Ожидание названия любимой игры пользователя
waiting_for_gta_activity = {}  # Ожидание ответа что нравится делать в GTA
# Новые состояния для игр
number_game_active = {}  # {chat_id: target_number}
number_game_attempts = {}  # {chat_id: attempts_count}

# Загадки с вариантами ответов
RIDDLES = [
    {
        "question": "Зимой и летом одним цветом. Что это?",
        "options": ["Снег", "Елка", "Трава", "Небо"],
        "correct": 1  # Индекс правильного ответа (начиная с 0)
    },
    {
        "question": "Без рук, без ног, а ворота отворяет. Что это?",
        "options": ["Ветер", "Дождь", "Солнце", "Собака"],
        "correct": 0
    },
    {
        "question": "Что можно увидеть с закрытыми глазами?",
        "options": ["Свет", "Сон", "Темноту", "Звезды"],
        "correct": 1
    },
    {
        "question": "У кого есть шляпа без головы и нога без сапога?",
        "options": ["Пугало", "Гриб", "Стул", "Дерево"],
        "correct": 1
    },
    {
        "question": "Что становится больше, если его поставить вверх ногами?",
        "options": ["Стакан", "Цифра 6", "Дом", "Человек"],
        "correct": 1
    }
]

STANDARD_QUESTIONS = {
    "Как тебя зовут?": lambda msg: bot.send_message(msg.chat.id, "Меня зовут TestBot. А как тебя зовут?", reply_markup=None),
    "Что ты любишь делать?": lambda msg: bot.send_message(msg.chat.id, "Люблю помогать людям и отвечать на вопросы."),
    "Какие твои любимые игры?": lambda msg: handle_favorite_games(msg),
    "На чём ты любишь кататься?": lambda msg: bot.send_message(msg.chat.id, "Я предпочитаю кататься на велосипеде по городским улицам."),
    "Есть ли у тебя домашнее животное?": lambda msg: handle_pets(msg),
    "Как дела?": lambda msg: bot.send_message(msg.chat.id, "У меня всё отлично! А у тебя как дела?", reply_markup=None),
    "🎮 Игры": lambda msg: show_games_menu(msg),
}

# Создание обычной клавиатуры
def create_keyboard(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup

# Создание inline клавиатуры
def create_inline_keyboard(buttons_data):
    markup = types.InlineKeyboardMarkup()
    for button_text, callback_data in buttons_data:
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    return markup

# Показать меню игр
def show_games_menu(msg):
    games_buttons = [
        ("🔢 Угадай число", "game_number"),
        ("🧩 Загадки", "game_riddles"),
        ("🔙 Назад в меню", "back_main")
    ]
    markup = create_inline_keyboard(games_buttons)
    bot.send_message(msg.chat.id, "🎮 Выбери игру:", reply_markup=markup)

# Начать игру "Угадай число"
def start_number_game(chat_id):
    target_number = random.randint(1, 100)
    number_game_active[chat_id] = target_number
    number_game_attempts[chat_id] = 0
    
    bot.send_message(
        chat_id, 
        "🔢 Я загадал число от 1 до 100!\nУ тебя есть 7 попыток. Попробуй угадать!"
    )

# Обработка попытки угадать число
def process_number_guess(message):
    chat_id = message.chat.id
    try:
        guess = int(message.text)
        target = number_game_active[chat_id]
        attempts = number_game_attempts[chat_id] + 1
        number_game_attempts[chat_id] = attempts
        
        if guess == target:
            bot.send_message(
                chat_id, 
                f"🎉 Поздравляю! Ты угадал число {target} с {attempts} попытки!\n\n"
                "Хочешь сыграть ещё?",
                reply_markup=create_inline_keyboard([
                    ("🔄 Играть снова", "game_number"),
                    ("🔙 В меню игр", "games_menu")
                ])
            )
            number_game_active.pop(chat_id, None)
            number_game_attempts.pop(chat_id, None)
        elif attempts >= 7:
            bot.send_message(
                chat_id,
                f"😔 Попытки закончились! Загаданное число было {target}.\n\n"
                "Попробуем ещё раз?",
                reply_markup=create_inline_keyboard([
                    ("🔄 Играть снова", "game_number"),
                    ("🔙 В меню игр", "games_menu")
                ])
            )
            number_game_active.pop(chat_id, None)
            number_game_attempts.pop(chat_id, None)
        elif guess < target:
            bot.send_message(
                chat_id, 
                f"📈 Больше! Попытка {attempts}/7"
            )
        else:
            bot.send_message(
                chat_id, 
                f"📉 Меньше! Попытка {attempts}/7"
            )
    except ValueError:
        bot.send_message(chat_id, "❗ Пожалуйста, введи число от 1 до 100!")

# Показать случайную загадку
def show_random_riddle(chat_id):
    riddle = random.choice(RIDDLES)
    riddle_buttons = []
    
    for i, option in enumerate(riddle["options"]):
        riddle_buttons.append((option, f"riddle_{i}_{riddle['correct']}"))
    
    markup = create_inline_keyboard(riddle_buttons + [("🔙 В меню игр", "games_menu")])
    bot.send_message(chat_id, f"🧩 Загадка:\n\n{riddle['question']}", reply_markup=markup)

# Обработка вопроса о любимых играх
def handle_favorite_games(msg):
    bot.send_message(msg.chat.id, "Моя любимая игра — 'StarCraft II', люблю стратегии.")
    follow_up_question = "А какая у тебя любимая игра?"
    bot.send_message(msg.chat.id, follow_up_question)
    waiting_for_user_favorite_game[msg.chat.id] = True  # Ожидаем название любимой игры

# Обработка ответа о любимой игре пользователя
def process_user_favorite_game(message):
    user_game = message.text.strip()
    chat_id = message.chat.id
    
    # Проверяем, упоминается ли GTA в названии игры
    if "gta" in user_game.lower() or "гта" in user_game.lower():
        response = f"{user_game} — отличная игра! Я люблю гонять на машинах в этой игре, а что тебе нравится там делать?"
        bot.send_message(chat_id, response)
        waiting_for_user_favorite_game.pop(chat_id, None)  # Больше не ожидаем название игры
        waiting_for_gta_activity[chat_id] = True  # Ожидаем ответ о том, что нравится делать в GTA
    else:
        response = f"{user_game} — потрясающая игра! 🎮"
        bot.send_message(chat_id, response)
        waiting_for_user_favorite_game.pop(chat_id, None)  # Завершаем диалог

# Обработка ответа о деятельности в GTA
def process_gta_activity(message):
    user_activity = message.text.strip()
    chat_id = message.chat.id
    response = "Неплохо! 👍"
    bot.send_message(chat_id, response)
    waiting_for_gta_activity.pop(chat_id, None)  # Завершаем диалог

# Обработка домашних животных
def handle_pets(msg):
    bot.send_message(msg.chat.id, "Нет животных, но если бы были, выбрал бы кота.")
    follow_up_question = "А у тебя есть животное?"
    bot.send_message(msg.chat.id, follow_up_question)
    waiting_for_animal_answer[msg.chat.id] = True

def process_animal_response(message):
    user_answer = message.text.lower().strip()
    chat_id = message.chat.id
    
    if user_answer.startswith('да'):
        follow_up_question = "Какое у тебя животное?"
        bot.send_message(chat_id, follow_up_question)
        waiting_for_animal_answer.pop(chat_id, None)
        waiting_for_specific_animal[chat_id] = True
    elif user_answer.startswith('нет') or user_answer.startswith('не'):
        response = "У меня тоже."
        bot.send_message(chat_id, response)
        waiting_for_animal_answer.pop(chat_id, None)
    else:
        bot.send_message(chat_id, "Не поняла твой ответ. Скажи либо 'Да' или 'Нет'.")

def process_specific_animal_response(message):
    animal_type = message.text.capitalize()
    chat_id = message.chat.id
    response = f"Круто, я бы тоже хотела иметь {animal_type.lower()}!"
    bot.send_message(chat_id, response)
    follow_up_question = f"Как зовут твоего {animal_type.lower()}?"
    bot.send_message(chat_id, follow_up_question)
    waiting_for_specific_animal.pop(chat_id, None)
    waiting_for_animal_name[chat_id] = True

def process_animal_name_response(message):
    pet_name = message.text.capitalize()
    chat_id = message.chat.id
    response = f"Классное имя — {pet_name}!"
    bot.send_message(chat_id, response)
    waiting_for_animal_name.pop(chat_id, None)

# Обработчики команд
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я — TestBot. Начнем наше знакомство?",
        reply_markup=create_keyboard(STANDARD_QUESTIONS.keys())
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🤖 **TestBot - Помощь**

**Команды:**
• /start — начать общение с ботом
• /help — показать список команд
• /restart — перезагрузить сессию
• /games — открыть меню игр

**Игры:**
🔢 Угадай число (1-100)
🧩 Загадки с вариантами ответов

**Общение:**
Можешь задать мне вопросы о себе, моих увлечениях или просто поболтать!
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['games'])
def games_command(message):
    show_games_menu(message)

@bot.message_handler(commands=['restart'])
def restart_command(message):
    chat_id = message.chat.id
    # Очищаем все состояния
    states_to_clear = [
        waiting_for_name, waiting_for_greeting_response, waiting_for_animal_answer,
        waiting_for_specific_animal, waiting_for_animal_name, waiting_for_user_favorite_game,
        waiting_for_gta_activity, number_game_active, number_game_attempts
    ]
    for state in states_to_clear:
        state.pop(chat_id, None)
    
    bot.send_message(
        chat_id, 
        "🔄 Сессия перезагружена!", 
        reply_markup=create_keyboard(STANDARD_QUESTIONS.keys())
    )

# Обработчик inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "games_menu":
        bot.edit_message_text(
            "🎮 Выбери игру:",
            chat_id,
            call.message.message_id,
            reply_markup=create_inline_keyboard([
                ("🔢 Угадай число", "game_number"),
                ("🧩 Загадки", "game_riddles"),
                ("🔙 Назад в меню", "back_main")
            ])
        )
    
    elif call.data == "game_number":
        bot.edit_message_text(
            "🔢 Начинаем игру 'Угадай число'!",
            chat_id,
            call.message.message_id
        )
        start_number_game(chat_id)
    
    elif call.data == "game_riddles":
        bot.delete_message(chat_id, call.message.message_id)
        show_random_riddle(chat_id)
    
    elif call.data.startswith("riddle_"):
        parts = call.data.split("_")
        chosen_answer = int(parts[1])
        correct_answer = int(parts[2])
        
        if chosen_answer == correct_answer:
            response = "🎉 Правильно! Отлично!"
        else:
            response = "❌ Неправильно, но не расстраивайся!"
        
        bot.edit_message_text(
            f"{call.message.text}\n\n{response}",
            chat_id,
            call.message.message_id,
            reply_markup=create_inline_keyboard([
                ("🔄 Ещё загадку", "game_riddles"),
                ("🔙 В меню игр", "games_menu")
            ])
        )
    
    elif call.data == "normal_chat":
        bot.edit_message_text(
            "💬 Отлично! Теперь можешь задать мне любой вопрос:",
            chat_id,
            call.message.message_id
        )
        # Отправляем обычную клавиатуру для вопросов
        bot.send_message(
            chat_id,
            "Выбери вопрос:",
            reply_markup=create_keyboard(STANDARD_QUESTIONS.keys())
        )
    
    elif call.data == "back_main":
        bot.edit_message_text(
            "Привет! Я — TestBot. Начнем наше знакомство?",
            chat_id,
            call.message.message_id
        )
        # Отправляем обычную клавиатуру для вопросов
        bot.send_message(
            chat_id,
            "Выбери вопрос:",
            reply_markup=create_keyboard(STANDARD_QUESTIONS.keys())
        )
    
    bot.answer_callback_query(call.id)

# Основной обработчик текстовых сообщений
@bot.message_handler(content_types=["text"])
def handle_any_message(message):
    chat_id = message.chat.id
    
    # Проверяем активную игру "Угадай число"
    if chat_id in number_game_active:
        process_number_guess(message)
        return
    
    # Проверяем состояния ожидания ответов (ВАЖНО: это должно быть ПЕРЕД проверкой стандартных вопросов)
    if waiting_for_name.get(chat_id, False):
        name = message.text.strip()
        bot.send_message(chat_id, f"Рад знакомству, {name}! Давай дружить?", reply_markup=None)
        waiting_for_name.pop(chat_id, None)
        waiting_for_greeting_response[chat_id] = True
    
    elif waiting_for_greeting_response.get(chat_id, False):
        text = message.text.lower().strip()
        if text in ["давай", "хорошо"]:
            bot.send_message(chat_id, "😊 Ура! Я рада нашей дружбе!")
            waiting_for_greeting_response.pop(chat_id, None)
        elif text in ["нет", "не хочу", "не хочу дружить"]:
            bot.send_message(chat_id, "🙁 Жаль... Может, ещё поговорим позже?")
            waiting_for_greeting_response.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "Не поняла твой ответ. Напиши 'давай' или 'нет'.")
    
    elif waiting_for_user_favorite_game.get(chat_id, False):
        process_user_favorite_game(message)
    elif waiting_for_gta_activity.get(chat_id, False):
        process_gta_activity(message)
    elif waiting_for_animal_answer.get(chat_id, False):
        process_animal_response(message)
    elif waiting_for_specific_animal.get(chat_id, False):
        process_specific_animal_response(message)
    elif waiting_for_animal_name.get(chat_id, False):
        process_animal_name_response(message)
    
    # Обычная обработка стандартных вопросов (только если нет активных состояний ожидания)
    elif message.text in STANDARD_QUESTIONS:
        handler = STANDARD_QUESTIONS[message.text]
        if callable(handler):
            handler(message)
            if message.text == "Как тебя зовут?":
                waiting_for_name[chat_id] = True
    
    else:
        bot.send_message(
            chat_id,
            "🤔 Такой вопрос отсутствует. Попробуй выбрать из списка ниже:",
            reply_markup=create_keyboard(STANDARD_QUESTIONS.keys())
        )

# Запуск бота
print("🤖 Бот запущен с новыми играми и inline клавиатурами!")
bot.polling(non_stop=True)