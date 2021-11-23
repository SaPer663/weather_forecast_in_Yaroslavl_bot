from parser import get_filled_dictionary

import telebot

from config import token_key

BOT_TOKEN = token_key
bot = telebot.TeleBot(BOT_TOKEN)
DATABASE = get_filled_dictionary()
last_date = next(reversed(DATABASE))


@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(
        message.chat.id,
        (f'Привет, я бот прогноза погоды до {last_date} в Ярославле.'
         ' Отправь мне дату в формате день.месяц (02.08)'
         ' и я дам прогноз погоды')
    )


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.text in DATABASE.keys():
        result = DATABASE[message.text]
        response = (f"{result['data-text']},"
                    " температура днём {result['temp_max']},"
                    " ночь до {result['temp_min']}")
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Введите правильную дату')


if __name__ == '__main__':
    bot.polling(none_stop=True)
