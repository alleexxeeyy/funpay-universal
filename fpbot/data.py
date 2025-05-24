import json
from datetime import datetime
import os

class Data:

    def __init__(self):
        self.initialized_users_path = 'fpbot/bot_data/initialized_users.json'
        self.stats_path = 'fpbot/bot_data/current_stats.json'
        self.categories_raise_time_path = 'fpbot/bot_data/categories_raise_time.json'
        self.events_next_time_path = 'fpbot/bot_data/events_next_time.json'
        self.saved_lots_path = 'fpbot/bot_data/saved_lots.json'


    def get_initialized_users(self) -> list[str]:
        """ Возвращает массив инициализированных в диалоге пользователей """

        folder_path = os.path.dirname(self.initialized_users_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Если файл существует - открываем его
        try:
            with open(self.initialized_users_path, 'r', encoding="utf-8") as f:
                initialized_users = json.load(f)
        # Иначе создаём его
        except:
            with open(self.initialized_users_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            initialized_users = []
        finally:
            return initialized_users
             
    def get_categories_raise_time(self) -> dict:
        """ Возвращает словарь со следующими временами поднятия категорий """

        folder_path = os.path.dirname(self.categories_raise_time_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Если файл существует - открываем его
        try:
            with open(self.categories_raise_time_path, 'r', encoding="utf-8") as f:
                categories_raise_time = json.load(f)
        # Иначе создаём его
        except:
            with open(self.categories_raise_time_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
            categories_raise_time = {}
        finally:
            return categories_raise_time 
            
    def get_events_next_time(self) -> dict:
        """ Возвращает словарь со следующими временами для выполнения нужных событий """

        folder_path = os.path.dirname(self.events_next_time_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Если файл существует - открываем его
        try:
            with open(self.events_next_time_path, 'r', encoding="utf-8") as f:
                events_next_time = json.load(f)
        # Иначе создаём его
        except:
            default_events_next_time = {
                "save_lots_next_time": datetime.now().isoformat(),
                "completed_orders_notify_next_time": datetime.now().isoformat(),
                "set_actual_lot_prices_next_time": datetime.now().isoformat(),
            }
            with open(self.events_next_time_path, 'w', encoding='utf-8') as f:
                json.dump(default_events_next_time, f, indent=4, ensure_ascii=False)
            events_next_time = default_events_next_time
        finally:
            return events_next_time

    def get_saved_lots(self) -> list[int]:
        """ Возвращает массив сохранённых в программе лотов аккаунта """

        folder_path = os.path.dirname(self.saved_lots_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Если файл существует - открываем его
        try:
            with open(self.saved_lots_path, 'r', encoding="utf-8") as f:
                get_saved_lots = json.load(f)
        # Иначе создаём его
        except:
            default_saved_lots = {
                "active": [],
                "inactive": []
            }
            with open(self.saved_lots_path, 'w', encoding='utf-8') as f:
                json.dump(default_saved_lots, f, indent=4, ensure_ascii=False)
            get_saved_lots = default_saved_lots
        finally:
            return get_saved_lots

    
    def update_initialized_users(self, new_data):
        """
            Перезаписывает данные об инициализированных пользователей в файле

            :param new_data: Новый массив данных
        """

        with open(self.initialized_users_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    def update_categories_raise_time(self, new_data):
        """
            Перезаписывает данные о текущих категориях и их следующем времени поднятия в файле

            :param new_data: Новый словарь данных
        """

        with open(self.categories_raise_time_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    def update_events_next_time(self, new_data):
        """
            Перезаписывает данные о текущих следующих временах для важных ивентов в файле

            :param new_data: Новый словарь данных
        """

        with open(self.events_next_time_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    def update_saved_lots(self, new_data):
        """
            Перезаписывает данные о сохранённых лотах

            :param new_data: Новый словарь данных
        """

        with open(self.saved_lots_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)