from typing import Dict

from telebot import TeleBot
from telebot.types import LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup

import admin_notification
from admin_notification import NotificationData
from config import provider_token, checkout_error, card_disclaimer

bot: TeleBot = None
order_items = dict()
notification_by_id: Dict[int, NotificationData] = dict()


def pay(chat_id, user_id, notification_id):
    if user_id not in order_items:
        return

    prices = []
    for _, item in order_items[user_id].items():
        if item.amount > 0:
            prices.append(LabeledPrice('{} ({} шт)'.format(item.name, item.amount), item.price * item.amount * 100))

    bot.send_message(chat_id, card_disclaimer, parse_mode='Markdown')
    bot.send_invoice(chat_id, title='Рожковый рай',
                     description='Самые вкусные рожки в галактике',
                     provider_token=provider_token,
                     currency='rub',
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='time-machine-example',
                     invoice_payload=notification_id)


def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message=checkout_error)


def got_payment(message):
    payment = message.successful_payment
    notification_id = int(payment.invoice_payload)

    if notification_id not in notification_by_id:
        return

    admin_notification.update_paid(notification_by_id[notification_id])

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
    bot.send_message(message.chat.id, 'Спасибо за покупку!', parse_mode='Markdown', reply_markup=markup)
