from random import randrange

import requests


class VK:
    """ Класс для работы с VK API"""
    BASE_URL = 'https://api.vk.com/method/'
    BASE_VK_URL = 'https://vk.com/'

    def __init__(self, access_token, version='5.199'):
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_city_id(self, city):
        """Получение id города
        Args:
            city (str): Название города, для которого необходимо получить id.
        Returns:
            int: Идентификатор города в базе данных VK.
        Raises:
            ValueError: Если не удалось найти город.
        """
        params = {'q': city}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}database.getCities', params=params)
        find_cities = response.json()['response']
        if find_cities['count'] > 0:
            find_city_id = find_cities['items'][0]['id']
        else:
            raise ValueError('Не удалось найти город')

        return find_city_id

    def get_photos(self, owner_id, album_id='profile', count=3):
        """Получение фотографий пользователя
        Args:
            owner_id (int): Идентификатор пользователя VK, фотографии которого нужно получить.
            album_id (str): Идентификатор альбома, из которого нужно получить фотографии. По умолчанию 'profile'.
            count (int): Количество фотографий, которое нужно вернуть. По умолчанию 3.
        Returns:
            list: Список словарей с информацией о фотографиях пользователя
        """
        params = {'owner_id': owner_id, 'album_id': album_id, 'extended': 1, 'photo_sizes': 1}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}photos.get', params=params)
        user_photos = response.json()['response']['items']
        photos_with_likes = {}

        for user_photo in user_photos:
            photos_with_likes[user_photo['id']] = user_photo['likes']['count']

        user_photo_list = sorted(photos_with_likes.items(), key=lambda item: item[1], reverse=True)
        photo_list_count = user_photo_list[0:count]

        return photo_list_count

    def get_user_params(self, user_with_params):
        """" Получение необходимых параметров пользователя
        Args:
            user_with_params (dict): Словарь с информацией о пользователе.

        Returns:
            dict: Словарь с информацией о пользователе.
        """
        find_user = {}
        find_user_photos = self.get_photos(user_with_params['id'])
        find_user['name_and_last_name'] = f"{user_with_params['first_name']} {user_with_params['last_name']}"
        find_user['urs'] = f"{self.BASE_VK_URL}id{user_with_params['id']}"
        find_user['photos'] = find_user_photos

        return find_user

    def get_user_info(self, user_id):
        """Получение информации о пользователе
        Args:
            user_id:
                int: Идентификатор пользователя VK
        Returns:
            dict: Словарь с информацией о пользователе
        """
        params = {'user_ids': user_id}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}users.get', params=params)

        return response.json()

    def search_user(self, user_params):
        """Поиск пользователя
        Args:
            user_params:
                dict: Словарь с параметрами поиска
        Returns:
            dict: Словарь с информацией о случайно выбранном пользователе
        """
        city_id = self.get_city_id(user_params['city'])
        params = {'age_from': user_params['age_from'], 'city': city_id, 'sex': user_params['sex']}
        if user_params['age_to'] != 0:
            params['age_to'] = user_params['age_to']
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}users.search', params=params)
        find_users = response.json()['response']['items']
        random_user = find_users[randrange(0, len(find_users) - 1)]

        while True:
            if not random_user['is_closed']:
                break
            else:
                random_user = find_users[randrange(0, len(find_users) - 1)]

        return random_user
