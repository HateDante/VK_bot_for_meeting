import json
from random import randrange

import vk_api

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from VK.VK_searcher import VK


def send_message(user_id, vk_session, text='', json_keyboard=None):
    values = {
        'user_id': user_id,
        'random_id': randrange(10 ** 7),
        'message': text
    }
    if json_keyboard is not None:
        values['keyboard'] = json_keyboard

    vk_session.method('messages.send', values)


def get_credentials():
    with open('credentials.json', 'r', encoding='utf8') as f:
        credentials = json.load(f)
    return credentials


def bot_start():

    age_from = 0
    age_to = 0
    city = ''
    sex = 0
    next_step = ''

    credentials = get_credentials()

    vk_session = vk_api.VkApi(token=credentials['GroupServiceToken'])
    longpoll = VkLongPoll(vk_session)

    vk_connection = VK(credentials['PersonalAccessToken'], credentials['AppID'])

    for event in longpoll.listen():
        if not(event.from_user and not event.from_me):
            continue
        if event.type != VkEventType.MESSAGE_NEW:
            continue
        event_text = event.text
        if event_text == 'Закончить':
            text_msg = 'На сегодня закончили. Удачи в самостоятельном поиске, человек!'
            vk_keyboard = VkKeyboard()
            send_message(event.user_id, vk_session, text_msg, vk_keyboard.get_empty_keyboard())
            next_step = ''
        elif event_text == 'Погнали':
            text_msg = 'Погоди, сначала нужно указать желаемый возраст в формате \'от\'-\'до\''\
                       ' (например, 25-45) либо точный возраст чисилом (например, 18)'
            vk_keyboard = VkKeyboard()
            vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
            send_message(event.user_id, vk_session, text_msg, vk_keyboard.get_keyboard())
            next_step = 'age'
        elif next_step == 'age':
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
                send_message(event.user_id, vk_session, text_msg)
                continue
            else:
                text_msg = 'Отлично! Теперь укажи свой город, желательно без сокращения. Вариант "Питер" не катит.'
                send_message(event.user_id, vk_session, text_msg)
                next_step = 'city'
        elif next_step == 'city':
            city = event_text
            text_msg = 'Замечательно. Осталось совсем чуть-чуть! Укажи свой пол: 1 - женский, 2 - мужской.'
            send_message(event.user_id, vk_session, text_msg)
            next_step = 'sex'
        elif next_step == 'sex':
            try:
                sex = int(event_text)
                if sex != 1 and sex != 2:
                    raise ValueError
            except ValueError:
                text_msg = 'Не понял последнее сообщение. Укажи свой пол: 1 - женский, 2 - мужской.'
                send_message(event.user_id, vk_session, text_msg)
                continue
            else:
                text_msg = 'У тебя получилось! Теперь жми кнопку "Начать поиск" чтобы, собственно, его начать.'\
                            'Удачи, человек!'
                vk_keyboard = VkKeyboard(True)
                vk_keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
                send_message(event.user_id, vk_session, text_msg, vk_keyboard.get_keyboard())
                next_step = ''
        elif ((event_text == 'Начать поиск' or event_text == 'Следующий')
              and age_from != 0 and city != '' and sex != 0):
            vk_keyboard = VkKeyboard()
            vk_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
            vk_keyboard.add_button('Добавить в избранное', VkKeyboardColor.POSITIVE)
            vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
            find_user = vk_connection.search_user(age_from, age_to, city, sex)
            find_user_params = vk_connection.get_user_params(find_user)
            for key, value in find_user_params.items():
                if key == 'photos':
                    for photo in value:
                        send_message(event.user_id, vk_session, photo, vk_keyboard.get_keyboard())
                else:
                    send_message(event.user_id, vk_session, value, vk_keyboard.get_keyboard())
        elif event_text == 'Добавить в избранное':
            f = 0
            # find_user_id = find_user[id]
            # photos_list = find_user_params['photos']
            # дальше запись в БД
        else:
            vk_keyboard = VkKeyboard(True)
            vk_keyboard.add_button('Погнали', VkKeyboardColor.POSITIVE)
            text_msg = 'Жми кнопку \'Погнали\' чтобы начать поиск людей'
            send_message(event.user_id, vk_session, text_msg, vk_keyboard.get_keyboard())

