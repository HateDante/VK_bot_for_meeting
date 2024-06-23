import os
from random import randrange

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from DB.Model import create_session, add_user, add_favorite_user, add_photos, get_favorites
from VK.vk_searcher import VK


class VKBOT:
    """ Класс для создания бота
        Args:
            group_token(str) - ключ доступа группы VK
            personal_token(str) - ключ доступа пользователя VK"""

    def __init__(self, group_token=os.getenv('GROUPSERVICETOKEN'), personal_token=os.getenv('PERSONALACCESSTOKEN')):
        self.user_params = {'age_from': 0, 'age_to': 0, 'city': '', 'sex': 0}
        self.find_user = {'user_data': {}, 'user_params': {}}
        self.vk_session = vk_api.VkApi(group_token)
        self.vk_connection = VK(personal_token)
        self.session = create_session()

    def bot_start(self):
        """Запуск бота для взаимодействия пользователем в социальной сети VK.
         Бот использует VK API для получения сообщений от пользователей, обрабатывает их
         и выполняет соответствующие действия.
            Args:
                None. Параметры и токены используются из переменных окружения.
            Returns:
                None. Функция выполняется до тех пор, пока пользователь не нажмет кнопку "Закончить"."""
        longpoll = VkLongPoll(self.vk_session)
        current_step = ''

        for event in longpoll.listen():
            if not (event.from_user and not event.from_me):
                continue
            if event.type != VkEventType.MESSAGE_NEW:
                continue

            user_id = event.user_id
            request = event.text

            if current_step != '' and request != 'Закончить':
                current_step = self.input_params_event(user_id, request, current_step)
            elif request == 'Закончить':
                current_step = self.stop_event(user_id)
            elif request == 'Погнали':
                current_step = self.start_event(user_id)
            elif (request == 'Начать поиск' or request == 'Следующий') and self.user_params_fulfill():
                self.start_search(user_id)
            elif request == 'Добавить в избранное':
                self.add_to_favorite(user_id)
            elif request == 'Избранное':
                self.print_favorite_list(user_id)
            else:
                self.prepare_to_start(user_id)

        self.session.close()

    def send_message(self, user_id, text='', json_keyboard=None):
        """Отправка сообщения пользователю"""
        values = {
            'user_id': user_id,
            'random_id': randrange(10 ** 7),
            'message': text
        }
        if json_keyboard is not None:
            values['keyboard'] = json_keyboard

        self.vk_session.method('messages.send', values)

    def stop_event(self, user_id):
        """Завершение работы бота.
        Функция вызывается, когда пользователь нажимает кнопку "Закончить". После сообщения об окончании работы бота,
        клавиатура удаляется.
        Args:
            user_id(int): Уникальный идентификатор пользователя в VK.
        Returns:
            str: Пустая строка, означающая завершение работы бота."""
        text_msg = 'На сегодня закончили. Удачи в самостоятельном поиске, человек!'
        vk_keyboard = VkKeyboard()
        self.send_message(user_id, text_msg, vk_keyboard.get_empty_keyboard())
        current_step = ''
        return current_step

    def start_event(self, user_id):
        """Начать поиск
        Args:
            user_id(int): Уникальный идентификатор пользователя в VK.
        Returns:
            str: Сообщение о необходимости ввести возраст пользователя."""
        text_msg = 'Погоди, сначала нужно указать желаемый возраст в формате \'от\'-\'до\'' \
                   ' (например, 25-45) либо точный возраст числом (например, 18)'
        vk_keyboard = VkKeyboard()
        vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
        self.send_message(user_id, text_msg, vk_keyboard.get_keyboard())
        current_step = 'input age'
        return current_step

    def user_params_fulfill(self):
        """Проверка параметров, введенных пользователем
        Функция проверяет все ли параметры, необходимые для поиска, введены. Если нет - возвращает True.
        Returns:
            bool: Значение True, если хотя бы один параметр не заполнен, иначе False."""
        is_empty = False

        for value in self.user_params.values():
            if value == 0 or value == '':
                is_empty = True
                break
        return is_empty

    def input_params_event(self, user_id, request, current_step):
        """Ввод параметров поиска.
        На каждом шаге (`current_step`), функция запрашивает параметры поиска и обновляет словарь `user_params`.
        Args:
            user_id(int): Уникальный идентификатор пользователя в VK.
            request(str): Введенные пользователем данные.
            current_step(str): Текущий шаг ввода параметров поиска.
        Returns:
            str: Обновленное значение `current_step`, указывающее на следующий этап ввода параметров.
        Raises:
            ValueError: Если введено некорректное значение."""
        if current_step == 'input age':
            try:
                if '-' in request:
                    age_list = request.split('-')
                    self.user_params['age_from'] = int(age_list[0])
                    self.user_params['age_to'] = int(age_list[1])
                else:
                    self.user_params['age_from'] = int(request)
            except ValueError:
                text_msg = 'Указан некорректный возраст. Нужно указать желаемый возраст в формате "от"-"до"' \
                           ' (например, 25-45) либо точный возраст числом (например, 18)'
                self.send_message(user_id, text_msg)
            else:
                text_msg = 'Отлично! Теперь укажи свой город, желательно без сокращения. Вариант "Питер" не катит.'
                self.send_message(user_id, text_msg)
                current_step = 'input city'
        elif current_step == 'input city':
            self.user_params['city'] = request
            text_msg = 'Замечательно. Осталось совсем чуть-чуть! Укажи свой пол: 1 - женский, 2 - мужской.'
            self.send_message(user_id, text_msg)
            current_step = 'input sex'
        elif current_step == 'input sex':
            try:
                self.user_params['sex'] = int(request)
                if self.user_params['sex'] not in [1, 2]:
                    raise ValueError
            except ValueError:
                text_msg = 'Не понял последнее сообщение. Укажи свой пол: 1 - женский, 2 - мужской.'
                self.send_message(user_id, text_msg)
            else:
                text_msg = 'У тебя получилось! Теперь жми кнопку "Начать поиск" чтобы, собственно, его начать.' \
                           'Удачи, человек!'
                vk_keyboard = VkKeyboard(True)
                vk_keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
                self.send_message(user_id, text_msg, vk_keyboard.get_keyboard())
                current_step = ''
        return current_step

    def start_search(self, user_id):
        """Поиск пользователей в соответствии с введенными параметрами.
        Функция добавляет пользователя в базу данных, создает клавиатуру и начинает поиск пользователей.
        После получения данных о пользователях, выводит информацию и фото найденных пользователей.
        Args:
            user_id(int): Уникальный идентификатор пользователя в VK.
        Returns:
            None. Функция ничего не возвращает, но выводит ссылки на профиль и фото найденных пользователей."""
        add_user(self.session, user_id, self.user_params)
        vk_keyboard = VkKeyboard()
        vk_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
        vk_keyboard.add_button('Добавить в избранное', VkKeyboardColor.POSITIVE)
        vk_keyboard.add_line()
        vk_keyboard.add_button('Избранное', VkKeyboardColor.SECONDARY)
        vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
        self.find_user['user_data'] = self.vk_connection.search_user(self.user_params)
        self.find_user['user_params'] = self.vk_connection.get_user_params(self.find_user['user_data'])
        for key, value in self.find_user['user_params'].items():
            if key == 'photos':
                for photo in value:
                    self.send_message(user_id, photo, vk_keyboard.get_keyboard())
            else:
                self.send_message(user_id, value, vk_keyboard.get_keyboard())

    def add_to_favorite(self, user_id):
        """Добавление пользователя в избранное.
        Функция добавляет информацию о пользователе и его фотографиях в базу данных.
        Args:
            user_id(int): Уникальный идентификатор пользователя VK, который добавляет другого пользователя в избранное.
        Returns:
            None: Функция ничего не возвращает, но отправляет сообщение пользователю о результате добавления
            в избранное.
        Raises:
            Exception: Описывает ошибку, которая может возникнуть при добавлении пользователя в избранное."""
        try:
            find_user_id = self.find_user['user_data']['id']
            photos_list = self.find_user['user_params']['photos']
            add_favorite_user(self.session, user_id, find_user_id)
            add_photos(self.session, user_id, photos_list)
            text_msg = 'Пользователь и его фотографии добавлены в избранное.'
        except Exception as e:
            text_msg = f'Не удалось добавить пользователя в избранное: {e}'
        self.send_message(user_id, text_msg)

    def print_favorite_list(self, user_id):
        """Вывод списка всех пользователей, добавленных в избранное.
        Args:
            user_id(int): Уникальный идентификатор пользователя VK, запрашивающего список избранных.
        Returns:
            None: Функция ничего не возвращает, но выводит список избранных пользователях, сохраненных в базе данных.
            Или сообщение о том, что список пуст."""
        favorites_list = get_favorites(self.session, user_id)
        if favorites_list:
            text_msg = 'Список избранных пользователей:\n'
            for favorite in favorites_list:
                user_info = self.vk_connection.get_user_info(favorite.favorite_user_id)
                text_msg += (f"{user_info['response'][0]['first_name']} {user_info['response'][0]['last_name']} - "
                             f"{self.vk_connection.BASE_VK_URL}id{favorite.favorite_user_id}\n")
        else:
            text_msg = 'Список избранных пользователей пока пуст.'
            self.send_message(user_id, text_msg)

    def prepare_to_start(self, user_id):
        """Подготовка к началу поиска.
        Функция создает клавиатуру для VK бота и отправляет пользователю сообщение с предложением начать поиск.
        Args:
            user_id(int): Уникальный идентификатор пользователя VK, который начинает поиск.
        Returns:
            None: Функция ничего не возвращает, но отправляет пользователю сообщение и создает
            кнопку для начала поиска."""
        vk_keyboard = VkKeyboard(True)
        vk_keyboard.add_button('Погнали', VkKeyboardColor.POSITIVE)
        text_msg = 'Жми кнопку \'Погнали\' чтобы начать поиск людей'
        self.send_message(user_id, text_msg, vk_keyboard.get_keyboard())
