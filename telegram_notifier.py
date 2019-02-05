# -*- coding: utf-8 -*-
from telegram import Bot
import config


class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    def send_message(self, message):
        self.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=message)


if __name__ == "__main__":
    TelegramNotifier().send_message('message')
