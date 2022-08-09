import os
import shutil
import json
from yauploader import YaUploader
from vk import VK
import configparser
from pathlib import Path


def main(photos_count=5):
    config = configparser.ConfigParser()
    config.read(f'{str(Path.home())}/settings.ini')
    # создание объектов vk и uploader
    vk = VK(config['VK'])
    uploader = YaUploader(config['YANDEX'])
    # проверка существования директории
    you_need_to_create_a_directory = not os.path.exists(vk.id)
    if you_need_to_create_a_directory:
        os.mkdir(vk.id)
    # получение фотографий пользователя vk(по умолчанию 5)
    photos_info = vk.photos_get(vk.id.split('[')[1][2:-1]).json()['response']['items'][:photos_count]
    # получение списка для записи в json файл и списка с именами фото и url
    information_about_saved_photos, file_name_and_url = vk.getting_lists_of_information_by_files(photos_info)
    # загрузка файлов на яндекс диск
    uploader.upload_files_to_disk(file_name_and_url, vk.id)
    # запись в json файл, загрузка его на яндекс диск и удаление с локального устройства
    with open(vk.id + '/information_about_saved_photos.json', 'w') as json_file:
        json.dump(information_about_saved_photos, json_file)
    uploader.upload_a_file_using_request(vk.id + '/information_about_saved_photos.json',
                                         vk.id + '/information_about_saved_photos.json')
    shutil.rmtree(vk.id)


if __name__ == '__main__':
    main(10)
