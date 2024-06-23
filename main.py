"""Основной модуль для запуска VK бота.
Создает экземпляр бота и осуществляет его запуск."""
from VK.vk_bot import VKBOT

if __name__ == '__main__':
    vk_bot = VKBOT()
    vk_bot.bot_start()
