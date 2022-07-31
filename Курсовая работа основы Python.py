#!/usr/bin/env python
# coding: utf-8

# Курсовая работа - основы языка программирования Python

# In[1]:


import requests
import time
import os
from progress.bar import IncrementalBar
import shutil
import json


# In[2]:


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.base_url = 'https://api.vk.com/'

    def users_info(self, user_ids):
        """
        Метод получает базовую информацию о пользователе
        """
        method_name = 'users.get'
        params = {
            'user_ids': user_ids
        }
        return requests.get(f'{self.base_url}method/{method_name}', params={**self.params, **params})

    def photos_get(self, owner_id):
        method_name = 'photos.get'
        params = {
            'owner_id': owner_id,
            'album_id': 'wall',
            'count':    1000,
            'extended': 1
        }
        return requests.get(f'{self.base_url}method/{method_name}', params={**self.params, **params})


# In[3]:


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def upload_a_file_using_request(self, file_path, file_path_yadisk, replace=False):
        """
        загрузка файла на яндекс диск с помощью библиотеки request
        in:
        file_path - путь к файлу который нужно загрузить
        file_path_yadisk - путь к файлу на яндекс диске
        replace - заменить файл или нет
        """
        base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type':   'application/json',
                   'Accept':         'application/json',
                   'Authorization': f'OAuth {self.token}'}

        response = requests.get(f'{base_url}/upload?path={file_path_yadisk}&overwrite={replace}', headers=headers).json()
        with open(file_path, 'rb') as f:
            try:
                requests.put(response['href'], files={'file': f})
            except KeyError:
                print(response)

    def create_directory(self, path: str):
        base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type':   'application/json',
                   'Accept':         'application/json',
                   'Authorization': f'OAuth {self.token}'}
        requests.put(f'{base_url}?path={path}', headers=headers)

    def the_directory_exists(self, path: str) -> bool:
        base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        response = requests.get(f'{base_url}?path={path}', headers=headers)
        return response.status_code != 404


# In[4]:


def save_data(file_name, file_data):
    file = open(file_name, 'bw')
    for chunk in file_data.iter_content(4096):
        file.write(chunk)
    file.close()


# In[5]:


def get_objects():
    """
    метод загружает токены, получает id пользователя vk и возвращает нужные объекты
    """
    # получение токенов из файла requiremеnts.txt
    with open('/home/jgjytrwetgdgn/Рабочий стол/обучение/нетология/python разработчик/модуль 1/курсовая работа - основы python/requiremеnts.txt', 'r') as tokens: YANDEX_TOKEN, VK_TOKEN = tokens.read().split('\n')[:2]
    # создание объектов vk и uploader и получение id пользователя vk
    uploader = YaUploader(YANDEX_TOKEN)
    vk = VK(VK_TOKEN, input('id пользователя vk->'))
    # получение базовой информации о пользователе
    basic_user_information = vk.users_info(vk.id).json()['response'][0]
    vk.id = basic_user_information['first_name'] + '_' +             basic_user_information['last_name'] + '[id' +             str(basic_user_information['id']) + ']'
    return uploader, vk


# In[6]:


def getting_lists_of_information_by_files(photos_info):
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
            photo_info['file_name'] = likes_count + '_' + str(photo['date']) + '.jpg'
        information_about_saved_photos.append(photo_info)
    photos_info.clear()
    return information_about_saved_photos, file_name_and_url


# In[7]:


def upload_files_to_yadisk(file_name_and_url, vk, uploader):
    l = len(file_name_and_url.items())
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for count, item in enumerate(file_name_and_url.items(), start=1):
        file_name, url = item
        file_path = vk.id + '/' + file_name + '.jpg'
        save_data(file_path, requests.get(url))
        you_need_to_create_a_directory = not uploader.the_directory_exists(vk.id)
        if you_need_to_create_a_directory: uploader.create_directory(vk.id)
        # загружаем файл на яндекс диск
        uploader.upload_a_file_using_request(file_path, file_path, replace=True)
        time.sleep(0.1)
        os.remove(file_path)
        printProgressBar(count - 1 + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)


# In[9]:


def main(photos_count=5):
    # получаем объекты vk и uploader
    uploader, vk = get_objects()
    # проверка существования директории
    you_need_to_create_a_directory = not os.path.exists(vk.id)
    if you_need_to_create_a_directory: os.mkdir(vk.id)
    # получение фотографий пользователя vk(по умолчанию 5)
    photos_info = vk.photos_get(vk.id.split('[')[1][2:-1]).json()['response']['items'][:photos_count]
    # получение списка для записи в json файл и списка с именами фото и url
    information_about_saved_photos, file_name_and_url = getting_lists_of_information_by_files(photos_info)
    # загрузка файлов на яндекс диск
    upload_files_to_yadisk(file_name_and_url, vk, uploader)
    # запись в json файл, загрузка его на яндекс диск и удаление с локального устройства
    with open(vk.id + '/information_about_saved_photos.json', 'w') as json_file:
        json.dump(information_about_saved_photos, json_file)
    uploader.upload_a_file_using_request(vk.id + '/information_about_saved_photos.json',
                                         vk.id + '/information_about_saved_photos.json', replace=True)
    shutil.rmtree(vk.id)


if __name__ == '__main__':
    main(10)


# In[8]:


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

