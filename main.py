from pprint import pprint
from VK_searcher import VK


if __name__ == '__main__':
    app_id = '51950153'
    access_token = ('vk1.a.yyAmN6tRkSZAvgvwgmXqKs1thIGRZsiGmPoK05WWtoaBxFwYZb8QTGkNKA6B_QlP75W5VHd7gC_qDUc5DjwVPKBN0CX'
                    '-ynzToUoLzY82iqn5I939uKuH2wRNWXEsZ_Fphiqv7yKzak1jWBXSv0pABVvyrxaPkcsj0kFLEZCout_'
                    'gvoDb8aJQbhDCuoqKffCq')
    vk_connection = VK(access_token, app_id)
    find_user = vk_connection.get_user_match_params()
    pprint(find_user)
