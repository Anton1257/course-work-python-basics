import requests
from progressbar import printProgressBar
import time
import os


class YaUploader:
    def __init__(self, config):
        self.token = config['token']

    def save_data(self, file_name, file_data):
        file = open(file_name, 'bw')
        for chunk in file_data.iter_content(4096):
            file.write(chunk)
        file.close()

    def upload_a_file_using_request(self, file_path, file_path_yadisk):
        """
        загрузка файла на яндекс диск с помощью библиотеки request
        in:
        file_path - путь к файлу который нужно загрузить
        file_path_yadisk - путь к файлу на яндекс диске
        """
        base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}

        response = requests.get(f'{base_url}/upload?path={file_path_yadisk}', headers=headers).json()
        with open(file_path, 'rb') as f:
            try:
                requests.put(response['href'], files={'file': f})
            except KeyError:
                print(response)

    def upload_files_to_disk(self, file_name_and_url, vk_id):
        # создание прогресс бара
        l = len(file_name_and_url.items())
        printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
        for count, item in enumerate(file_name_and_url.items(), start=1):
            file_name, url = item
            file_path = vk_id + '/' + file_name + '.jpg'
            self.save_data(file_path, requests.get(url))
            self.check_directory(vk_id)
            # загружаем файл на яндекс диск
            self.upload_a_file_using_request(file_path, file_path)
            time.sleep(0.1)
            os.remove(file_path)
            printProgressBar(count, l, prefix='Progress:', suffix='Complete', length=50)

    def check_directory(self, path: str):
        base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        response = requests.get(f'{base_url}?path={path}', headers=headers)
        if response.status_code == 404:
            requests.put(f'{base_url}?path={path}', headers=headers)