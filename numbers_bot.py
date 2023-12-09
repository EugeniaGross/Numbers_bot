from datetime import date
import os
import requests
import sys

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import googletrans


def fact_translate(fact):
    translator = googletrans.Translator()
    return translator.translate(fact, 'ru').text


def say_hello(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['Факт о сегодняшнем дне', 'Математический факт'],
         ['Факт о годе', 'Факт о дате'],
         ['Интересный факт']],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text=(
            f'Привет, {name}! Хочешь узнать чем знаменит сегодняшний день в истории? '
            f'Нажми на кнопку "Факт о сегодняшнем дне". '
            f'Хочешь узнать интересные факты о числах? '
            f'Введи интересующее тебя число и нажми одну из кнопок! '
            f'Если хочешь узнать факт о дате, введи дату и месяц через пробел числами.'
        ),
        reply_markup=button
    )


def math_fact(update, context):
    chat = update.effective_chat
    number = context.user_data['number'].split()
    if len(number) == 1:
        math_fact_en = get_fact(number[0], 'math')
        math_fact_ru = fact_translate(math_fact_en)
        context.bot.send_message(chat_id=chat.id, text=math_fact_ru)
    else:
        update.message.reply_text(
            'Если хотите узнать математический факт введите одно число:'
        )
        raise IndexError('Пользователь ввел много чисел')


def year_fact(update, context):
    chat = update.effective_chat
    year = context.user_data['number'].split()
    if len(year) == 1:
        year_fact_en = get_fact(year[0], 'year')
        year_fact_ru = fact_translate(year_fact_en)
        context.bot.send_message(chat_id=chat.id, text=year_fact_ru)
    else:
        update.message.reply_text(
            'Если хотите узнать факт о годе введите одно число:'
        )
        raise IndexError('Пользователь ввел много чисел')


def date_fact(update, context):
    chat = update.effective_chat
    try:
        numbers = (context.user_data['number']).split()
        day = numbers[0]
        month = numbers[1]
    except Exception:
        update.message.reply_text(
            'Введи дату и месяц через пробел числами ДД ММ:'
        )
        raise ValueError('Пользователь ввел неверный формат данных')
    date_fact_en = get_date_fact(day, month)
    date_fact_ru = fact_translate(date_fact_en)
    context.bot.send_message(chat_id=chat.id, text=date_fact_ru)


def today_fact(update, context):
    chat = update.effective_chat
    date_today = date.today()
    day = date_today.strftime("%d")
    month = date_today.strftime("%m")
    day_fact_en = get_date_fact(day, month)
    dat_fact_ru = fact_translate(day_fact_en)
    context.bot.send_message(chat_id=chat.id, text=dat_fact_ru)


def trivia_fact(update, context):
    chat = update.effective_chat
    number = context.user_data['number'].split()
    if len(number) == 1:
        trivia_fact_en = get_fact(number[0], 'trivia')
        trivia_fact_ru = fact_translate(trivia_fact_en)
        context.bot.send_message(chat_id=chat.id, text=trivia_fact_ru)
    else:
        update.message.reply_text(
            'Если хотите узнать интересный факт факт введите одно число:'
        )
        raise IndexError('Пользователь ввел много чисел')


def save_number(update, context):
    number_list = update.message.text.split()
    if len(number_list) > 2:
        update.message.reply_text('Ты ввел много чисел, '
            'если хочешь узнать интересные или '
            'математические факты или факт о годе введи одно число! '
            'Если хотите узнать факт о дате '
            'введите дату и месяц через пробел числами ДД ММ!')
        raise IndexError('Пользователь ввел много чисел')
    for number in number_list:
        if not number.isdigit():
            update.message.reply_text('Введи число, '
            'если хочешь узнать интересные или '
            'математические факты или факт о годе! '
            'Если хочешь узнать факт о дате '
            'введи дату и месяц через пробел числами ДД ММ!')
            raise TypeError('Пользователь ввел другой тип данных')
    number = update.message.text
    context.user_data['number'] = number


def get_date_fact(day, month):
    response = requests.get(f'http://numbersapi.com/{month}/{day}/date')
    return response.text


def get_fact(number, type_fact):
    response = requests.get(f'http://numbersapi.com/{number}/{type_fact}')
    return response.text


def main():
    load_dotenv()
    token = os.getenv('TOKEN')
    if not token:
        sys.exit('Переменные окружения не доступны')
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', say_hello))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Факт о сегодняшнем дне'), today_fact))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Математический факт'), math_fact))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Факт о годе'), year_fact))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Факт о дате'), date_fact))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Интересный факт'), trivia_fact))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, save_number))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
