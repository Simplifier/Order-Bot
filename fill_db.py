import os

import telebot

import config
from SQLighter import SQLighter


def fill(db, bot, chat_id):
    for file in os.listdir('pics/'):
        if db.get_image('pics/' + file) is not None:  # db has this file
            continue

        if not file.lower().endswith(('.jpg', '.jpeg', '.gif', '.png')):  # not an image
            continue

        with open('pics/' + file, 'rb') as f:
            print(f.name)
            msg = bot.send_photo(chat_id, f)

            db.add_photo('pics/' + file, msg.photo[0].file_id, msg.photo[1].file_id)

    print('complete')


if __name__ == '__main__':
    bot = telebot.TeleBot(config.token, threaded=False)
    db = SQLighter(config.database_name)
    bot.polling(none_stop=True)

    # fill_db.fill(db, bot, message.chat.id)
