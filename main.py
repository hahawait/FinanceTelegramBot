import telebot
import gspread
# import os  # Для использования переменных окружения, хранящих API телеграм бота и google таблицы
from telebot import types  # Для указания типов
from config import tg_bot_token, googlesheet_id



bot = telebot.TeleBot(tg_bot_token)
gc = gspread.service_account()

@bot.message_handler(commands=['help', 'start'])
def starthelp(message):
    bot.reply_to(message,
                 'Привет, я буду записивать ваши расходы в таблицу. Введите расход через дефис в виде [КАТЕГОРИЯ-ЦЕНА]:')

@bot.message_handler(content_types=['text'])
def AddDataToTheTableAndStatistic(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Самая дорогая покупка')
    btn2 = types.KeyboardButton('Самая дешевая покупка')
    markup.add(btn1, btn2)

    # Открываем нашу таблицу, в worksheet будет первый лист таблицы
    sh = gc.open_by_key(googlesheet_id)
    worksheet = sh.sheet1

    if message.text == 'Самая дорогая покупка':
        MaxPrice = max(worksheet.col_values(3)[1:]) # Ищем max в колонке с ценами
        cell = worksheet.find(MaxPrice)
        MaxPriceData = worksheet.row_values(cell.row) # Сохраняем найденную строку
        bot.send_message(message.chat.id, '\n'.join(map(str, MaxPriceData))) # Выводим

    elif message.text == 'Самая дешевая покупка':
        MinPrice = min(worksheet.col_values(3)[1:])
        cell = worksheet.find(MinPrice)
        MinPriceData = worksheet.row_values(cell.row)
        bot.send_message(message.chat.id, '\n'.join(map(str, MinPriceData)))

    else:
        try:
            today = date.today().strftime("%d.%m.%Y")

            #  разделяем сообщение на 2 части, категория и цена
            category, price = message.text.split("-", 1)
            text_message = f'На {today} в таблицу расходов добавлена запись: категория {category}, сумма {price} руб'
            bot.send_message(message.chat.id, text_message)

            # открываем Google таблицу и добавляем запись
            sh = gc.open_by_key(googlesheet_id)
            sh.sheet1.append_row([today, category, price])
        except:
            # если пользователь ввел неправильную информацию, оповещаем его и просим вводить повторно
            bot.send_message(message.chat.id, 'ОШИБКА! Неправильный формат данных!')

        bot.send_message(message.chat.id, 'Введите расход через дефис в виде [КАТЕГОРИЯ-ЦЕНА]:')


if __name__ == '__main__':
    bot.polling(none_stop=True)