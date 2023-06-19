import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from main import VkinderBack
from vkinder_db import *


class VkinderInterface():
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_vkinder = VkinderBack(access_token)
        self.params = {}
        self.matches_found = []
        self.offset = 0

    def messages_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

    def check_profile(self, event):
        one_profile = self.matches_found.pop()
        while check_user(engine, event.user_id, one_profile["id"]):
            if self.matches_found:
                one_profile = self.matches_found.pop()
            else:
                self.offset += 10
                self.matches_found = self.vk_vkinder.search_matches(self.params, self.offset)
                one_profile = self.matches_found.pop()

        return one_profile

    def add_photo(self, one_profile):
        photos = self.vk_vkinder.get_photos(one_profile['id'])
        photo_string = ''
        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
        return photo_string

    def message_sorter(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_vkinder.get_profile_info(event.user_id)
                    self.messages_send(
                        event.user_id, f'Привет, {self.params["name"]}\n'
                        f'Для поиска наберите слово поиск или нажмите п')
                elif event.text.lower() == 'поиск' or event.text.lower() == 'п':
                    if self.params.get('city') is None:
                        self.messages_send(
                            event.user_id, f'Для начала поиска необходимо указать город')
                        while True:
                            for event in self.longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    city = event.text.title()
                                    self.params['city'] = city
                                    self.messages_send(
                                        event.user_id, f'Отлично! Будем искать в городе {city}')
                                    break
                            break

                    self.messages_send(
                        event.user_id, 'Начинаю поиск')
                    if self.matches_found:
                        one_profile = self.check_profile(event)
                        attachment = self.add_photo(one_profile)
                    else:
                        self.matches_found = self.vk_vkinder.search_matches(
                            self.params, self.offset)
                        one_profile = self.check_profile(event)
                        attachment = self.add_photo(one_profile)
                        self.offset += 10

                    self.messages_send(
                        event.user_id,
                        f'ФИО: {one_profile["name"]}\n ссылка: vk.com/id{one_profile["id"]}',
                        attachment=attachment
                        )

                    add_user(engine, event.user_id, one_profile["id"])

                    self.messages_send(
                        event.user_id, f'Для продолжения поиска наберите слово поиск или нажмите п')

                elif event.text.lower() == 'пока' or event.text.lower() == 'спасибо':
                    self.messages_send(
                        event.user_id, 'Удачных знакомств! Пока!')
                else:
                    self.messages_send(
                        event.user_id, 'Vkinder не распознал команду')


if __name__ == '__main__':
    bot_interface = VkinderInterface(community_token, access_token)
    bot_interface.message_sorter()
