import json
from datetime import datetime
import os

class Data:
    INITIALIZED_USERS_PATH = 'fpbot/bot_data/initialized_users.json'
    CATEGORIES_RAISE_TIME_PATH = 'fpbot/bot_data/categories_raise_time.json'
    EVENTS_NEXT_TIME_PATH = 'fpbot/bot_data/events_next_time.json'
    SAVED_LOTS_PATH = 'fpbot/bot_data/saved_lots.json'

    def get_initialized_users(self) -> list[str]:
        """ Получает содержимое initialized_users.json """
        folder_path = os.path.dirname(Data.INITIALIZED_USERS_PATH)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        try:
            with open(Data.INITIALIZED_USERS_PATH, 'r', encoding="utf-8") as f:
                initialized_users = json.load(f)
        except:
            with open(Data.INITIALIZED_USERS_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            initialized_users = []
        finally:
            return initialized_users
             
    def get_categories_raise_time(self) -> dict:
        """ Получает содержимое categories_raise_time.json """
        folder_path = os.path.dirname(Data.CATEGORIES_RAISE_TIME_PATH)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        try:
            with open(Data.CATEGORIES_RAISE_TIME_PATH, 'r', encoding="utf-8") as f:
                categories_raise_time = json.load(f)
        except:
            with open(Data.CATEGORIES_RAISE_TIME_PATH, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
            categories_raise_time = {}
        finally:
            return categories_raise_time 
            
    def get_events_next_time(self) -> dict:
        """ Получает содержимое events_next_time.json """
        folder_path = os.path.dirname(Data.EVENTS_NEXT_TIME_PATH)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        try:
            with open(Data.EVENTS_NEXT_TIME_PATH, 'r', encoding="utf-8") as f:
                events_next_time = json.load(f)
        except:
            default_events_next_time = {
                "save_lots_next_time": datetime.now().isoformat(),
            }
            with open(Data.EVENTS_NEXT_TIME_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_events_next_time, f, indent=4, ensure_ascii=False)
            events_next_time = default_events_next_time
        finally:
            return events_next_time

    def get_saved_lots(self) -> list[int]:
        """ Получает содержимое saved_lots.json """
        folder_path = os.path.dirname(Data.SAVED_LOTS_PATH)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        try:
            with open(Data.SAVED_LOTS_PATH, 'r', encoding="utf-8") as f:
                get_saved_lots = json.load(f)
        except:
            default_saved_lots = {
                "active": [],
                "inactive": []
            }
            with open(Data.SAVED_LOTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_saved_lots, f, indent=4, ensure_ascii=False)
            get_saved_lots = default_saved_lots
        finally:
            return get_saved_lots

    
    def set_initialized_users(self, new_data):
        """ Перезаписывает данные в initialized_users.json """
        with open(Data.INITIALIZED_USERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    def set_categories_raise_time(self, new_data):
        """ Перезаписывает данные в categories_raise_time.json """
        with open(Data.CATEGORIES_RAISE_TIME_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    def set_events_next_time(self, new_data):
        """ Перезаписывает данные в events_next_time.json """
        with open(Data.EVENTS_NEXT_TIME_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    def set_saved_lots(self, new_data):
        """ Перезаписывает данные в new_data.json """
        with open(Data.SAVED_LOTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)