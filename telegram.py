import telebot
from config import tkn, id_chat


class TelegaBot:
    def __init__(self):
        self.token = tkn
        self.bot = telebot.TeleBot(self.token)
        self.captcha_txt = ''
        self.id_chat = str(id_chat)

    def send_photo(self):
        with open('captcha.png', 'rb') as file:
            captcha = file.read()
        self.bot.send_photo(id_chat, captcha)

    def handler_captcha(self):
        self.send_photo()

        @self.bot.message_handler(content_types = ['text'])
        def enter_captcha(message):
            self.captcha_txt = message.text
            print(self.captcha_txt)
            self.close_bot()

        self.run()

    def run(self):
        self.bot.polling(non_stop = True, skip_pending = True)

    def close_bot(self):
        self.bot.stop_polling()

    def __del__(self):
        print('Экземпляр бота отработал')
