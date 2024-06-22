from random import randrange
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from DB.Model import add_user, add_favorite_user, add_photos, get_favorites


def send_message(user_id, vk_session, text='', json_keyboard=None):
    """Отправка сообщения пользователю"""
    values = {
        'user_id': user_id,
        'random_id': randrange(10 ** 7),
        'message': text
    }
    if json_keyboard is not None:
        values['keyboard'] = json_keyboard

    vk_session.method('messages.send', values)


def stop_event(user_id, vk_session):
    """Завершение работы бота.
    Функция вызывается, когда пользователь нажимает кнопку "Закончить". После сообщения об окончании работы бота,
    клавиатура удаляется.
    Args:
        user_id(int): Уникальный идентификатор пользователя в VK.
        vk_session(vk_api.VkApi): Активная сессия VK API для отправки сообщений.
    Returns:
        str: Пустая строка, означающая завершение работы бота."""
    text_msg = 'На сегодня закончили. Удачи в самостоятельном поиске, человек!'
    vk_keyboard = VkKeyboard()
    send_message(user_id, vk_session, text_msg, vk_keyboard.get_empty_keyboard())
    current_step = ''
    return current_step


def start_event(user_id, vk_session):
    """Начать поиск
    Args:
        user_id(int): Уникальный идентификатор пользователя в VK.
        vk_session(vk_api.VkApi): Активная сессия VK API для отправки сообщений.
    Returns:
        str: Сообщение о необходимости ввести возраст пользователя."""
    text_msg = 'Погоди, сначала нужно указать желаемый возраст в формате \'от\'-\'до\'' \
               ' (например, 25-45) либо точный возраст числом (например, 18)'
    vk_keyboard = VkKeyboard()
    vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
    send_message(user_id, vk_session, text_msg, vk_keyboard.get_keyboard())
    current_step = 'input age'
    return current_step


def user_params_fulfill(user_params):
    """Проверка параметров, введенных пользователем
    Функция проверяет все ли параметры, необходимые для поиска, введены. Если нет - возвращает True.
    Args:
        user_params: dict: Словарь, где ключи - это названия параметров, а значения - данные, введенные пользователем.
    Returns:
        bool: Значение True, если хотя бы один параметр не заполнен, иначе False."""
    is_empty = False

    for value in user_params.values():
        if value == 0 or value == '':
            is_empty = True
            break
    return is_empty


def input_params_event(request, current_step, user_params, user_id, vk_session):
    """Ввод параметров поиска.
    На каждом шаге (`current_step`), функция запрашивает параметры поиска и обновляет словарь `user_params`.
    Args:
        request(str): Введенные пользователем данные.
        current_step(str): Текущий шаг ввода параметров поиска.
        user_params(dict): Словарь с параметрами пользователя.
        user_id(int): Уникальный идентификатор пользователя в VK.
        vk_session(vk_api.VkApi): Активная сессия VK API для отправки сообщений.
    Returns:
        str: Обновленное значение `current_step`, указывающее на следующий этап ввода параметров.
    Raises:
        ValueError: Если введено некорректное значение."""
    if current_step == 'input age':
        try:
            if '-' in request:
                age_list = request.split('-')
                user_params['age_from'] = int(age_list[0])
                user_params['age_to'] = int(age_list[1])
            else:
                user_params['age_from'] = int(request)
        except ValueError:
            text_msg = 'Указан некорректный возраст. Нужно указать желаемый возраст в формате "от"-"до"' \
                       ' (например, 25-45) либо точный возраст числом (например, 18)'
            send_message(user_id, vk_session, text_msg)
        else:
            text_msg = 'Отлично! Теперь укажи свой город, желательно без сокращения. Вариант "Питер" не катит.'
            send_message(user_id, vk_session, text_msg)
            current_step = 'input city'
    elif current_step == 'input city':
        user_params['city'] = request
        text_msg = 'Замечательно. Осталось совсем чуть-чуть! Укажи свой пол: 1 - женский, 2 - мужской.'
        send_message(user_id, vk_session, text_msg)
        current_step = 'input sex'
    elif current_step == 'input sex':
        try:
            user_params['sex'] = int(request)
            if user_params['sex'] not in [1, 2]:
                raise ValueError
        except ValueError:
            text_msg = 'Не понял последнее сообщение. Укажи свой пол: 1 - женский, 2 - мужской.'
            send_message(user_id, vk_session, text_msg)
        else:
            text_msg = 'У тебя получилось! Теперь жми кнопку "Начать поиск" чтобы, собственно, его начать.' \
                       'Удачи, человек!'
            vk_keyboard = VkKeyboard(True)
            vk_keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
            send_message(user_id, vk_session, text_msg, vk_keyboard.get_keyboard())
            current_step = ''
    return current_step


def start_search(session, user_id, user_params, vk_connection, vk_session, find_user):
    """Поиск пользователей в соответствии с введенными параметрами.
    Функция добавляет пользователя в базу данных, создает клавиатуру и начинает поиск пользователей.
    После получения данных о пользователях, выводит информацию и фото найденных пользователей.
    Args:
        session(Session): Сессия базы данных для добавления пользователя.
        user_id(int): Уникальный идентификатор пользователя в VK.
        user_params(dict): Словарь с параметрами поиска, заданными пользователем.
        vk_connection(VkConnection): Объект для взаимодействия с VK API.
        vk_session(vk_api.VkApi): Активная сессия VK API для отправки сообщений.
        find_user(dict): Словарь для хранения данных о найденных пользователях и параметрах поиска.
    Returns:
        None. Функция ничего не возвращает, но выводит ссылки на профиль и фото найденных пользователей."""
    add_user(session, user_id, user_params)
    vk_keyboard = VkKeyboard()
    vk_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
    vk_keyboard.add_button('Добавить в избранное', VkKeyboardColor.POSITIVE)
    vk_keyboard.add_line()
    vk_keyboard.add_button('Избранное', VkKeyboardColor.SECONDARY)
    vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
    find_user['user_data'] = vk_connection.search_user(user_params)
    find_user['user_params'] = vk_connection.get_user_params(find_user['user_data'])
    for key, value in find_user['user_params'].items():
        if key == 'photos':
            for photo in value:
                send_message(user_id, vk_session, photo, vk_keyboard.get_keyboard())
        else:
            send_message(user_id, vk_session, value, vk_keyboard.get_keyboard())


def add_to_favorite(session, user_id, vk_session, find_user):
    """Добавление пользователя в избранное.
    Функция добавляет информацию о пользователе и его фотографиях в базу данных.
    Args:
        session(Session): Сессия базы данных для работы с данными пользователя.
        user_id(int): Уникальный идентификатор пользователя VK, который добавляет другого пользователя в избранное.
        vk_session(vk_api.VkApi): Активная сессия VK API, используется для отправки уведомлений пользователю.
        find_user(dict): Словарь с данными о пользователе, которого нужно добавить в избранное (id и фото).
    Returns:
        None: Функция ничего не возвращает, но отправляет сообщение пользователю о результате добавления в избранное.
    Raises:
        Exception: Описывает ошибку, которая может возникнуть при добавлении пользователя в избранное."""
    try:
        find_user_id = find_user['user_data']['id']
        photos_list = find_user['user_params']['photos']
        add_favorite_user(session, user_id, find_user_id)
        add_photos(session, user_id, photos_list)
        text_msg = 'Пользователь и его фотографии добавлены в избранное.'
    except Exception as e:
        text_msg = f'Не удалось добавить пользователя в избранное: {e}'
    send_message(user_id, vk_session, text_msg)


def print_favorite_list(session, user_id, vk_connection, vk_session):
    """Вывод списка всех пользователей, добавленных в избранное.
    Args:
        session(Session): Сессия базы данных для работы с данными пользователя.
        user_id(int): Уникальный идентификатор пользователя VK, запрашивающего список избранных.
        vk_connection(VkConnection): Объект для взаимодействия с VK API и получения информации о пользователях.
        vk_session(vk_api.VkApi): Активная сессия VK API, используется для отправки сообщений пользователю.
    Returns:
        None: Функция ничего не возвращает, но выводит список избранных пользователях, сохраненных в базе данных.
        Или сообщение о том, что список пуст."""
    favorites_list = get_favorites(session, user_id)
    if favorites_list:
        text_msg = 'Список избранных пользователей:\n'
        for favorite in favorites_list:
            user_info = vk_connection.get_user_info(favorite.favorite_user_id)
            text_msg += (f"{user_info['response'][0]['first_name']} {user_info['response'][0]['last_name']} - "
                         f"{vk_connection.BASE_VK_URL}id{favorite.favorite_user_id}\n")
        send_message(user_id, vk_session, text_msg)
    else:
        send_message(user_id, vk_session, 'Список избранных пользователей пока пуст.')


def prepare_to_start(user_id, vk_session):
    """Подготовка к началу поиска.
    Функция создает клавиатуру для VK бота и отправляет пользователю сообщение с предложением начать поиск.
    Args:
        user_id(int): Уникальный идентификатор пользователя VK, который начинает поиск.
        vk_session(vk_api.VkApi): Активная сессия VK API, используется для отправки сообщений пользователю.
    Returns:
        None: Функция ничего не возвращает, но отправляет пользователю сообщение и создает кнопку для начала поиска."""
    vk_keyboard = VkKeyboard(True)
    vk_keyboard.add_button('Погнали', VkKeyboardColor.POSITIVE)
    text_msg = 'Жми кнопку \'Погнали\' чтобы начать поиск людей'
    send_message(user_id, vk_session, text_msg, vk_keyboard.get_keyboard())
