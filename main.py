import json
import telebot
from telebot import types
import config
import about

api_token = config.info["token_api"]

bot = telebot.TeleBot(api_token)

@bot.message_handler(commands=["start"]) # Команда регистрации и приветствия
def send_start(message):
	register_user(message)
	bot.send_message(message.chat.id, "Привет, с помощью меня, ты легко сможешь отслеживать использования своих средств. Введи команду /help, чтобы узнать, что я могу!")

@bot.message_handler(commands=["help"]) # Просто помощь
def output_commands(message):
	bot.send_message(message.chat.id, about.commands)


@bot.message_handler(commands=["new", "add_account"]) # Добовление счета
def add_account(message):
	msg = bot.send_message(message.chat.id, "Отлично, теперь назовите новый счет!")
	bot.register_next_step_handler(msg, add_account)

@bot.message_handler(commands=["a", "all_account"]) # Вывод всех счетов
def all_account(message):
	bot.send_message(message.chat.id, "Сейчас я поочерёдно выведу все твои счета:")
	output_all_accounts(message)

@bot.message_handler(commands=["edit_account"]) # Смена имени счета
def edit_account(message):
	list_account = []
	keyboard = types.InlineKeyboardMarkup()
	data = read_data(message.chat.id)
	for i in data["accounts"]: # Жеский парсинг и создание инлайн кнопок вне зависимости от их кол-ва
		list_account.append(types.InlineKeyboardButton(text=i["nameAccount"], callback_data=f"edit_{i["nameAccount"]}"))
	keyboard.add(*list_account, row_width=1)
	bot.send_message(message.chat.id, "Пока что, ты можешь изменить только имя. Для начала выбери счёт: ", reply_markup=keyboard)

@bot.message_handler(commands=["b", "balance"]) # Вывод баланса
def output_balance(message):
	balance = 0
	data = read_data(message.chat.id)
	for i in data["accounts"]:
		balance += i["balance"]
	bot.send_message(message.chat.id, f"На всех твоих счетах, в общем: {balance} руб.")

@bot.message_handler(commands=["m", "minus"]) # Расходы
def add_minus(message):
	list_account = []
	keyboard = types.InlineKeyboardMarkup()
	data = read_data(message.chat.id)
	for i in data["accounts"]:
		list_account.append(types.InlineKeyboardButton(text=i["nameAccount"], callback_data=f"minus_{i["nameAccount"]}"))
	keyboard.add(*list_account, row_width=1)
	bot.send_message(message.chat.id, "Выбери счёт для регистрации расходов: ", reply_markup=keyboard)

@bot.message_handler(commands=["p", "plus"]) # Доходы
def add_plus(message):
	list_account = []
	keyboard = types.InlineKeyboardMarkup()
	data = read_data(message.chat.id)
	for i in data["accounts"]:
		list_account.append(types.InlineKeyboardButton(text=i["nameAccount"], callback_data=f"plus_{i["nameAccount"]}"))
	keyboard.add(*list_account, row_width=1)
	bot.send_message(message.chat.id, "Выбери счёт для регистрации доходов: ", reply_markup=keyboard)






# Обработка кнопок при изменении
@bot.callback_query_handler(func=lambda call: call.data in [f"edit_{i["nameAccount"]}" for i in read_data(call.message.chat.id)["accounts"]])
def choice_account(call):
	msg = bot.send_message(call.message.chat.id, "Теперь введи новое имя!")
	bot.register_next_step_handler(msg, edit_name, call.data)
# Обработка кнопок при расходах
@bot.callback_query_handler(func=lambda call: call.data in [f"minus_{i["nameAccount"]}" for i in read_data(call.message.chat.id)["accounts"]])
def choice_account(call):
	msg = bot.send_message(call.message.chat.id, "Сколько ты потратил?")
	bot.register_next_step_handler(msg, add_minus, call.data)
# Обработка кнопок при доходах
@bot.callback_query_handler(func=lambda call: call.data in [f"plus_{i["nameAccount"]}" for i in read_data(call.message.chat.id)["accounts"]])
def choice_account(call):
	msg = bot.send_message(call.message.chat.id, "Сколько ты получил?")
	bot.register_next_step_handler(msg, add_plus, call.data)



# Собственно сами исполняющие функции

def add_plus(message, call):
	id = message.chat.id
	data = read_data(id)
	for i in data["accounts"]:
		if f"plus_{i["nameAccount"]}" == call:
			i["balance"] = i["balance"] + int(message.text)
	write_data(id, data)

def add_minus(message, call):
	id = message.chat.id
	data = read_data(id)
	for i in data["accounts"]:
		if f"minus_{i["nameAccount"]}" == call:
			i["balance"] = i["balance"] - int(message.text)
	write_data(id, data)

def edit_name(message, call):
	id = message.chat.id
	data = read_data(id)
	for i in data["accounts"]:
		if f"edit_{i["nameAccount"]}" == call:
			i["nameAccount"] = message.text
			write_data(id, data)

def register_user(message):
	id = message.chat.id
	name = message.chat.username
	data = { 
			"userId" : id,
			"userName" : name,
			"count_accounts" : 0,
			"accounts" : [],
			"history" : []
	}
	write_data(id, data)

def read_data(id): # Просто сократил чуток кода и вывел запись и чтение файлов в отдельные функции
	with open(f"{id}.json", "r") as file:
		data = json.load(file)
		return data

def write_data(id, data):
	with open(f"{id}.json", "w") as file:
		json.dump(data, file, indent=4)

def add_account(message):
	id = message.chat.id
	name = message.text
	data = read_data(id)
	account = {
	"nameAccount" : name,
	"balance" : 0
	}
	data["accounts"].append(account)
	write_data(id, data)
	bot.send_message(message.chat.id, "Счёт успешно добавлен!")

def output_all_accounts(message):
	id = message.chat.id
	data = read_data(id)
	for i in data["accounts"]:
		bot.send_message(message.chat.id, f"Счёт: {i["nameAccount"]}, с текущим балансом: {i["balance"]} руб.\n")




bot.infinity_polling()
