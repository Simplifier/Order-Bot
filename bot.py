import telebot

import admin_notification
import basket
import config
import fill_db
import menu
import order
import payments
import user_notification
from SQLighter import SQLighter
from order import OrderStatus

bot = telebot.TeleBot(config.token, threaded=False)
db = SQLighter(config.database_name)

path_by_message_id = dict()
menu_items = dict()
order_items = dict()
chat_by_user = dict()

menu.bot = bot
menu.db = db
menu.path_by_message_id = path_by_message_id
menu.menu_items = menu_items
menu.chat_by_user = chat_by_user

admin_notification.bot = bot
admin_notification.order_items = order_items

payments.bot = bot
payments.order_items = order_items
payments.notification_by_id = admin_notification.notification_by_id

user_notification.bot = bot
user_notification.chat_by_user = chat_by_user
user_notification.order_items = order_items

order.bot = bot
order.menu_items = menu_items
order.order_items = order_items

basket.bot = bot
basket.menu_items = menu_items


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Посмотрите наше /menu')


@bot.message_handler(commands=['basket'])
def show_menu(message):
    basket.show(message, message.from_user.id)


@bot.message_handler(commands=['menu'])
def show_menu(message):
    menu.show(message, message.from_user.id)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    payments.checkout(pre_checkout_query)


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payments.got_payment(message)


@bot.message_handler(commands=['filldb'])
def fill_in_db(message):
    fill_db.fill(db, bot, message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "plus":
        menu.update_menu_item_amount(call, 1)
    elif call.data == "minus":
        menu.update_menu_item_amount(call, -1)
    elif call.data == "basket":
        basket.show(call.message, call.from_user.id)
    elif call.data == "clear":
        basket.clear(call)
        basket.show(call.message, call.from_user.id)
    elif call.data == "menu":
        menu.show(call.message, call.from_user.id)
    elif call.data == "confirm":
        order.confirm(call)
    elif call.data in (OrderStatus.IN_PROGRESS, OrderStatus.READY, OrderStatus.TAKEN):
        admin_notification.update(call)
    elif call.data.split('|')[0] == "pay":
        payments.pay(call.message.chat.id, call.from_user.id, call.data.split('|')[1])


if __name__ == '__main__':
    bot.polling(none_stop=True)
