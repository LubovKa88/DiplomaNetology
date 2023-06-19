import vk_api
from vk_api.exceptions import ApiError
from pprint import pprint
from datetime import datetime
from config import access_token


class VkinderBack:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)

    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id):

        try:
            profile_info, = self.vkapi.method('users.get',
                                              {'user_id': user_id,
                                               'fields': 'city,sex,relation,bdate'
                                               }
                                              )
        except ApiError as e:
            profile_info = {}
            print(f'error = {e}')

        result = {'user_id': user_id,
                  'name': (profile_info['first_name'] + ' ' + profile_info['last_name']) if
                  'first_name' in profile_info and 'last_name' in profile_info else None,
                  'sex': profile_info.get('sex'),
                  'city': profile_info.get('city')['title'] if profile_info.get('city') is not None else None,
                  'year': self._bdate_toyear(profile_info.get('bdate')),
                  'relation': profile_info.get('relation')
                  }
        return result

    def search_matches(self, params, offset):
        try:
            matches = self.vkapi.method('users.search',
                                        {
                                            'count': 10,
                                            'offset': offset,
                                            'hometown': params['city'],
                                            'sex': 1 if params['sex'] == 2 else 2,
                                            'has_photo': True,
                                            'age_from': params['year'] - 3,
                                            'age_to': params['year'] + 3,
                                            'relation': 1,
                                        }
                                        )
        except ApiError as e:
            matches = []
            print(f'error = {e}')

        found_matches = [{'name': item['first_name'] + " " + item['last_name'],
                          'id': item['id'],
                          } for item in matches['items'] if item['is_closed'] is False
                         ]

        return found_matches

    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get',
                                       {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        }
                                       )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        got_photos = [{'owner_id': item['owner_id'],
                       'id': item['id'],
                       'likes': item['likes']['count'],
                       'comments': item['comments']['count']
                       } for item in photos['items']
                      ]
        got_photos.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)
        return got_photos[:3]


if __name__ == '__main__':
    user_id = 2625151
    vkinder = VkinderBack(access_token)
    params = vkinder.get_profile_info(user_id)
    matches_found = vkinder.search_matches(params, 10)
    one_profile = matches_found.pop()
    photos = vkinder.get_photos(one_profile['id'])

    pprint(matches_found)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
