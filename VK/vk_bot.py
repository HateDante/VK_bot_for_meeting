import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from DB.Model import create_session
from VK.vk_bot_events import stop_event, start_event, input_params_event, user_params_fulfill, \
    start_search, add_to_favorite, print_favorite_list, prepare_to_start
from VK.vk_searcher import VK


def bot_start():
    user_params = {'age_from': 0, 'age_to': 0, 'city': '', 'sex': 0}
    find_user = {'user_data': [], 'user_params': {}}
    current_step = ''

    vk_session = vk_api.VkApi(token=os.getenv('GroupServiceToken'))
    longpoll = VkLongPoll(vk_session)
    vk_connection = VK(os.getenv('PersonalAccessToken'), os.getenv('AppID'))
    session = create_session()

    for event in longpoll.listen():
        if not (event.from_user and not event.from_me):
            continue
        if event.type != VkEventType.MESSAGE_NEW:
            continue

        request = event.text

        if current_step != '':
            current_step = input_params_event(request, current_step, user_params, event.user_id, vk_session)
        elif request == 'Закончить':
            current_step = stop_event(event.user_id, vk_session)
        elif request == 'Погнали':
            current_step = start_event(event.user_id, vk_session)
        elif (request == 'Начать поиск' or request == 'Следующий') and user_params_fulfill(user_params):
            start_search(session, event.user_id, user_params, vk_connection, vk_session, find_user)
        elif request == 'Добавить в избранное':
            add_to_favorite(session, event.user_id, vk_session, find_user)
        elif request == 'Избранное':
            print_favorite_list(session, event.user_id, vk_connection, vk_session)
        else:
            prepare_to_start(event.user_id, vk_session)

    session.close()
