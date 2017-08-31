from telebot import TeleBot

import order
from config import user_notification
from order import OrderStatus

bot: TeleBot = None
chat_by_user = dict()
order_items = dict()


def send(query, user_id):
    status = ''
    if query == OrderStatus.IN_PROGRESS:
        status = 'готовится'
    elif query == OrderStatus.READY:
        status = 'готов'
    elif query == OrderStatus.TAKEN:
        status = 'выдан'

    order_number = order.get_order_number(user_id)
    text = user_notification.format(order_number, status)
    user_id = user_id
    text += order.get_order_list(order_items[user_id])
    bot.send_message(chat_by_user[user_id], text, parse_mode='Markdown')
