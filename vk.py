import requests
from datetime import datetime


class VK:
    def __init__(self, config, version='5.131'):
        self.token = config['token']
        self.version = version
        self.id = input('Введите id пользователя vk -> ')
        self.params = {'access_token': self.token, 'v': self.version}
        self.base_url = 'https://api.vk.com/'
        # получение базовой информации о пользователе
        basic_user_information = self.users_info(self.id).json()['response'][0]
        self.id = basic_user_information['first_name'] + '_' + \
                  basic_user_information['last_name'] + '[id' + \
                  str(basic_user_information['id']) + ']'

    def users_info(self, user_ids):
        """
        Метод получает базовую информацию о пользователе
        """
        method_name = 'users.get'
        params = {
            'user_ids': user_ids
        }
        response = requests.get(f'{self.base_url}method/{method_name}', params={**self.params, **params})
        return response

    def photos_get(self, owner_id, album_id='profile'):
        method_name = 'photos.get'
        """
        in: owner_id - id пользователя vk
        Метод получает фотографии пользователя:
        по умолчанию - фотографии профиля(profile)
        возможные варианты:
        wall - фотографии со стены
        saved - сохраненные фотографии.
        Возвращается только с ключом доступа пользователя
        """
        params = {
            'owner_id': owner_id,
            'album_id': album_id,
            'count':    1000,
            'extended': 1
        }
        return requests.get(f'{self.base_url}method/{method_name}', params={**self.params, **params})

    def getting_lists_of_information_by_files(self, photos_info):
        file_name_and_url = {}
        information_about_saved_photos = []
        for count, photo in enumerate(photos_info, start=1):
            likes_count = str(photo['likes']['count'])
            height = str(photo['sizes'][-1]['height'])
            width = str(photo['sizes'][-1]['width'])
            photo_info = {
                'file_name': likes_count + '.jpg',
                'size': height + 'x' + width
            }
            if likes_count not in file_name_and_url:
                file_name_and_url[likes_count] = photo['sizes'][-1]['url']
            else:
                file_name_and_url[likes_count + '_' + str(photo['date'])] = photo['sizes'][-1]['url']
                current_date = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')
                photo_info['file_name'] = likes_count + '_' + current_date + '.jpg'
            information_about_saved_photos.append(photo_info)
        photos_info.clear()
        return information_about_saved_photos, file_name_and_url