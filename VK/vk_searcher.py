from random import randrange

import requests


class VK:
    BASE_URL = 'https://api.vk.com/method/'
    BASE_VK_URL = 'https://vk.com/'

    def __init__(self, access_token, app_id, version='5.199'):
        self.token = access_token
        self.id = app_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_city_id(self, city):

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
        params = {'owner_id': owner_id, 'album_id': album_id, 'extended': 0, 'count': count}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}photos.get', params=params)

        return response.json()['response']['items']

    def get_user_params(self, user_with_params):
        find_user = {}
        photo_list = []
        find_user_photos = self.get_photos(user_with_params['id'])

        for current_photo in find_user_photos:
            size_params = current_photo['sizes'][-1]['url']
            photo_list.append(size_params)

        find_user['name_and_last_name'] = f'{user_with_params['first_name']} {user_with_params['last_name']}'
        find_user['urs'] = f'{self.BASE_VK_URL}id{user_with_params['id']}'
        find_user['photos'] = photo_list

        return find_user

    def get_user_info(self, user_id):
        params = {'user_ids': user_id}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}users.get', params=params)

        return response.json()

    def search_user(self, user_params):
        city_id = self.get_city_id(user_params['city'])
        params = {'age_from': user_params['age_from'], 'city': city_id, 'sex': user_params['sex']}
        if user_params['age_to'] != 0:
            params['age_to'] = user_params['age_to']
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}users.search', params=params)
        find_users = response.json()['response']['items']
        random_user = find_users[randrange(0, len(find_users) - 1)]

        return random_user
