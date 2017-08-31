from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import admin_notification
import basket
from config import confirm_descr
from utils import format_price

bot: TeleBot = None
order_items = dict()
menu_items = dict()
order_number = 0
order_number_by_user = dict()


def get_order_list_and_cost(items):
    text = ''
    cost = 0

    for _, item in items.items():
        if item.amount > 0:
            text += '\n{}: {} шт'.format(item.name, item.amount)
            cost += item.price * item.amount
    text += '\nСтоимость заказа: {} руб'.format(format_price(cost))
    return text, cost


def get_order_list(items):
    text, cost = get_order_list_and_cost(items)
    return text


def reset_order_number():
    global order_number
    order_number = 0


def __generate_order_number(user_id):
    global order_number
    order_number += 1
    order_number_by_user[user_id] = order_number
    print('gent', user_id)
    return get_order_number(user_id)


def get_order_number(user_id):
    num = order_number_by_user[user_id]
    print('get', user_id)
    return str(num).zfill(3)


def confirm(call):
    user_id = call.from_user.id
    if user_id not in menu_items:
        # покажем пустую корзину, если нечего оформлять
        basket.show(call.message, user_id)
        return

    num = __generate_order_number(user_id)
    text = confirm_descr.format(num)
    order_list = get_order_list(menu_items[user_id])
    text += order_list

    order_items[user_id] = menu_items[user_id]
    basket.clear(call)
    print('confirm', call)

    msg = admin_notification.send(num, order_list, call)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Оплатить через Яндеск.Кассу', callback_data='pay|' + str(msg.message_id)))

    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)


class OrderStatus:
    IN_PROGRESS = 'in_progress'
    READY = 'ready'
    TAKEN = 'taken'
