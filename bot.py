#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import telebot
import requests
from config import token_key
from parser import get_filled_dictionary, json_file_read, json_file_update


BOT_TOKEN = token_key
bot = telebot.TeleBot(BOT_TOKEN)
dataBase = get_filled_dictionary()
last_date = next(reversed(dataBase))



@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id, f"Привет, я бот прогноза погоды до {last_date} в Ярославле. \
    Отправь мне дату в формате день.месяц (02.08) и я дам прогноз погоды")

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.text in dataBase.keys():
        result = dataBase[message.text]
        response = f"{result['data-text']}, температура днём {result['temp_max']}, ночь до {result['temp_min']}"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Введите правильную дату')
    

if __name__ == '__main__':
     bot.polling(none_stop=True)
