from typing import Dict

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import order
import user_notification
from config import admin_notification, admin_chat
from order import OrderStatus


class NotificationData:
    def __init__(self, message_id, user, order_number, order_list, status):
        self.message_id = message_id
        self.user = user
        self.order_number = order_number
        self.order_list = order_list
        self.status = status
        self.paid = False


bot: TeleBot = None
order_items = dict()
notification_by_id: Dict[int, NotificationData] = dict()


def send(order_number, order_list, call):
    text, markup = __generate(order_number, order_list, call.from_user, OrderStatus.IN_PROGRESS, False)
    msg = bot.send_message(admin_chat, text, parse_mode='Markdown', reply_markup=markup)
    notification_by_id[msg.message_id] = NotificationData(msg.message_id, call.from_user, order_number, order_list,
                                                          OrderStatus.IN_PROGRESS)
    return msg


def update(call):
    message_id = call.message.message_id
    if message_id not in notification_by_id:
        return

    print('update', call)
    note = notification_by_id[message_id]
    note.status = call.data
    user = note.user
    text, markup = __generate(note.order_number, note.order_list, note.user, note.status, note.paid)

    bot.edit_message_text(text, chat_id=admin_chat, message_id=message_id,
                          parse_mode='Markdown', reply_markup=markup)
    user_notification.send(call.data, user.id)

    if note.status == OrderStatus.TAKEN:
        order_items.pop(user.id, None)
        notification_by_id.pop(message_id, None)
        if len(order_items) == 0:
            order.reset_order_number()


def update_paid(notification: NotificationData):
    note = notification
    note.paid = True
    text, markup = __generate(note.order_number, note.order_list, note.user, note.status, note.paid)

    bot.edit_message_text(text, chat_id=admin_chat, message_id=note.message_id,
                          parse_mode='Markdown', reply_markup=markup)


def __generate(order_number, order_list, user, status, paid):
    name = user.first_name
    if user.last_name:
        name += user.last_name

    paid_text = ''
    if paid:
        paid_text = '(*Оплачен*)'
    text = admin_notification.format(order_number, paid_text, name)
    text += order_list
    text += '\nСтатус: '

    markup = InlineKeyboardMarkup()

    if status == OrderStatus.IN_PROGRESS:
        text += '`Готовится`'
        markup.add(InlineKeyboardButton('Готов', callback_data=OrderStatus.READY),
                   InlineKeyboardButton('Выдан', callback_data=OrderStatus.TAKEN))
    elif status == OrderStatus.READY:
        text += '*Готов*'
        markup.add(InlineKeyboardButton('Готовится', callback_data=OrderStatus.IN_PROGRESS),
                   InlineKeyboardButton('Выдан', callback_data=OrderStatus.TAKEN))
    elif status == OrderStatus.TAKEN:
        text += 'Выдан'

    return text, markup
