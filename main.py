import json
from random import randrange

import vk_api
from pprint import pprint

from vk_api.longpoll import VkLongPoll, VkEventType

from VK_searcher import VK

if __name__ == '__main__':
    with open('credentials.json', 'r', encoding='utf8') as f:
        credentials = json.load(f)

    vk_session = vk_api.VkApi(token=credentials['GroupServiceToken'])
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():

        if event.from_user:
            if event.type == VkEventType.MESSAGE_NEW:
                if event.text == 'Найди мне кого-нибудь':
                    vk_connection = VK(credentials['PersonalAccessToken'], credentials['AppID'])
                    find_user = vk_connection.get_user_match_params()

                    for key, value in find_user.items():
                        vk_session.method('messages.send', {
                            'user_id': event.user_id,
                            'random_id': randrange(10 ** 7),
                            'message': value
                        })
