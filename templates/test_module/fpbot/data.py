import json
from datetime import datetime
import os

class Data:
    """ Класс, собирающий данные модуля """

    def __init__(self):
        current_dir = os.path.dirname(__file__)
        self.some_data_path = os.path.join(current_dir, 'module_data', 'some_data.json')

    def get_some_data(self) -> dict:
        folder_path = os.path.dirname(self.some_data_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        try:
            with open(self.some_data_path, 'r', encoding="utf-8") as f:
                some_data = json.load(f)
        except Exception as e:
            with open(self.some_data_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
            some_data = {}
        finally:
            return some_data

    def update_some_data(self, new_data):
        with open(self.some_data_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)