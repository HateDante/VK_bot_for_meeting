import json
from random import randrange

import vk_api
from pprint import pprint

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from VK_searcher import VK


def send_message(user_id, text='', json_keyboard=None):
    values = {
        'user_id': user_id,
        'random_id': randrange(10 ** 7),
        'message': text
    }
    if json_keyboard is not None:
        values['keyboard'] = json_keyboard

    vk_session.method('messages.send', values)


if __name__ == '__main__':
    age_from = 0
    age_to = 0
    city = ''
    sex = 0
    next_msg = ''

    with open('credentials.json', 'r', encoding='utf8') as f:
        credentials = json.load(f)

    vk_session = vk_api.VkApi(token=credentials['GroupServiceToken'])
    longpoll = VkLongPoll(vk_session)

    vk_connection = VK(credentials['PersonalAccessToken'], credentials['AppID'])

    for event in longpoll.listen():
        if event.from_user and not event.from_me:
            if event.type == VkEventType.MESSAGE_NEW:
                event_text = event.text
                if event_text == 'Закончить':
                    text_msg = 'На сегодня закончили. Удачи в самостоятельном поиске, человек!'
                    send_message(event.user_id, text_msg,vk_keyboard.get_empty_keyboard())
                    next_msg = ''
                elif event_text == 'Погнали':
                    text_msg = 'Погоди, сначала нужно указать желаемый возраст в формате \'от\'-\'до\''\
                               ' (например, 25-45) либо точный возраст чисилом (например, 18)'
                    vk_keyboard = VkKeyboard(True)
                    vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
                    send_message(event.user_id, text_msg, vk_keyboard.get_keyboard())
                    next_msg = 'age'
                elif next_msg == 'age':
                    try:
                        if '-' in event_text:
                            age_list = event_text.split('-')
                            age_from = int(age_list[0])
                            age_to = int(age_list[1])
                        else:
                            age_from = int(event_text)
                    except ValueError:
                        text_msg = 'Указан некорректный возраст. Нужно указать желаемый возраст в формате "от"-"до"' \
                                   ' (например, 25-45) либо точный возраст чисилом (например, 18)'
                        send_message(event.user_id, text_msg)
                        continue
                    text_msg = 'Отлично! Теперь укажи свой город, желательно без сокращения. Вариант "Питер" не катит.'
                    send_message(event.user_id, text_msg)
                    next_msg = 'city'
                elif next_msg == 'city':
                    city = event_text
                    text_msg = 'Замечательно. Осталось совсем чуть-чуть! Укажи свой пол: 1 - женский, 2 - мужской.'
                    send_message(event.user_id, text_msg)
                    next_msg = 'sex'
                elif next_msg == 'sex':
                    try:
                        sex = int(event_text)
                    except ValueError:
                        text_msg = 'Не понял последнее сообщение. Укажи свой пол: 1 - женский, 2 - мужской.'
                        send_message(event.user_id, text_msg)
                        continue
                    text_msg = 'У тебя получилось! Теперь жми кнопку "Начать поиск" чтобы, собственно, его начать.'\
                                'Удачи, человек!'
                    vk_keyboard = VkKeyboard(True)
                    vk_keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
                    send_message(event.user_id, text_msg, vk_keyboard.get_keyboard())
                    next_msg = ''
                elif event_text == 'Начать поиск' and age_from != 0 and city != '' and sex != 0:
                    vk_keyboard = VkKeyboard()
                    vk_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
                    vk_keyboard.add_button('Добавить в избранное', VkKeyboardColor.POSITIVE)
                    vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
                    # сюда надо передавать параметры age_from, age_to, city и sex
                    find_user = vk_connection.get_user_match_params()
                    for key, value in find_user.items():
                        send_message(event.user_id, value, vk_keyboard.get_keyboard())
                else:
                    vk_keyboard = VkKeyboard(True)
                    vk_keyboard.add_button('Погнали', VkKeyboardColor.POSITIVE)
                    text_msg = 'Жми кнопку \'Погнали\' чтобы начать поиск людей'
                    send_message(event.user_id, text_msg, vk_keyboard.get_keyboard())
