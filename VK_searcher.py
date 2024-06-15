from random import randrange

import requests


class VK:
    BASE_URL = 'https://api.vk.com/method/'
    BASE_VK_URL = 'https://vk.com/'

    def __init__(self, access_token, id, version='5.199'):
        self.token = access_token
        self.id = f'id{id}'
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_user_info(self, user_id):
        params = {'user_ids': user_id}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}users.get', params=params)
        return response.json()

    def get_user_match_params(self):
        find_user = {}
        photo_list = []
        params = {'age_from': 18, 'age_to': 45, 'sex': 1, 'city': 2}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}users.search', params=params)
        find_users = response.json()['response']['items']
        random_user = find_users[randrange(0, len(find_users) - 1)]

        find_user_photos = self.get_photos(random_user['id'])

        for current_photo in find_user_photos:
            size_params = current_photo['sizes'][-1]['url']
            photo_list.append(size_params)

        find_user['name'] = random_user['first_name']
        find_user['lastname'] = random_user['last_name']
        find_user['urs'] = f'{self.BASE_VK_URL}id{random_user['id']}'
        find_user['photos'] = photo_list
        return find_user

    def get_photos(self, owner_id, album_id='profile', count=3):
        params = {'owner_id': owner_id, 'album_id': album_id, 'extended': 0, 'count': count}
        params.update(self.params)
        response = requests.get(f'{self.BASE_URL}photos.get', params=params)
        return response.json()['response']['items']
