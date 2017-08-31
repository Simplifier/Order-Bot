from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from SQLighter import SQLighter
from config import menu_descr, menu_item_descr
from utils import format_price

bot: TeleBot = None
db: SQLighter = None
path_by_message_id = dict()
menu_items = dict()
chat_by_user = dict()


def show(message, user_id):
    print(message.chat.first_name)
    chat_by_user[user_id] = message.chat.id

    bot.send_message(message.chat.id, menu_descr.format(message.chat.first_name))
    for row in db.get_all():
        bot.send_photo(message.chat.id, row['full_id'])

        if user_id in menu_items:
            basket = menu_items[user_id]
        else:
            basket = menu_items[user_id] = dict()

        path = row['path']
        if path in basket:
            markup = __create_menu_item_markup(basket[path].amount)
        else:
            markup = __create_menu_item_markup(0)
            basket[path] = MenuItem(0, row['price'], row['name'])

        msg = bot.send_message(message.chat.id,
                               menu_item_descr.format(row['name'], row['descr'], format_price(row['price'])),
                               parse_mode='Markdown',
                               reply_markup=markup)

        path_by_message_id[msg.message_id] = path


def update_menu_item_amount(call, delta):
    message = call.message
    if message.message_id not in path_by_message_id:
        return
    if call.from_user.id not in menu_items:
        return
    if path_by_message_id[message.message_id] not in menu_items[call.from_user.id]:
        return

    item = menu_items[call.from_user.id][path_by_message_id[message.message_id]]
    if delta < 0 and item.amount == 0:
        return

    item.amount += delta

    markup = __create_menu_item_markup(item.amount)
    bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id,
                                  reply_markup=markup)


def __create_menu_item_markup(item_amount):
    amount_text = '0'
    show_basket = False
    if item_amount > 0:
        show_basket = True
        amount_text = '{} шт'.format(item_amount)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('+', callback_data='plus'),
               InlineKeyboardButton(amount_text, callback_data='price'),
               InlineKeyboardButton('-', callback_data='minus'))
    if show_basket:
        markup.add(InlineKeyboardButton('Корзина', callback_data='basket'))

    return markup


class MenuItem:
    def __init__(self, amount, price, name):
        self.amount = amount
        self.price = price
        self.name = name
