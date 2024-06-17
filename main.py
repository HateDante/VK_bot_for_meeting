import json
from pprint import pprint
from VK_searcher import VK


if __name__ == '__main__':
    credentials = {}
    with open('credentials.json', 'r', encoding='utf8') as f:
        credentials = json.load(f)

    vk_connection = VK(credentials['PersonalAccessToken'], credentials['AppID'])
    find_user = vk_connection.get_user_match_params()
    pprint(find_user)
