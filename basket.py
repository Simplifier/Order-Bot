from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import order
from config import basket_empty

bot: TeleBot = None
menu_items = dict()


def show(message, user_id):
    text = '*У вас в корзине:*'
    if user_id in menu_items:
        list_text, cost = order.get_order_list_and_cost(menu_items[user_id])
        text += list_text
    else:
        cost = 0

    markup = InlineKeyboardMarkup()

    if cost > 0:
        markup.add(InlineKeyboardButton('Оформить заказ', callback_data='confirm'))
        markup.add(InlineKeyboardButton('Очистить корзину', callback_data='clear'),
                   InlineKeyboardButton('Меню', callback_data='menu'))
    else:
        text = basket_empty
        markup.add(InlineKeyboardButton('Меню', callback_data='menu'))

    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)


def clear(call):
    menu_items[call.from_user.id] = dict()
