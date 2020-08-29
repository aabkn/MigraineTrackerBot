import pymongo
import pandas as pd
from datetime import date
from config import mongo_host


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(mongo_host)
        self.db = self.client['migraine_bot']

    def insert_user(self, chat_id, username):
        users_table = self.db['users']
        users_table.update({'chat_id': chat_id}, {'chat_id': chat_id, 'username': username}, upsert=True)

    def get_username(self, chat_id):
        users_table = self.db['users']
        return users_table.find_one({'chat_id': chat_id})['username']

    def set_state(self, chat_id, state):
        state_table = self.db['user_state']
        state_table.update({'chat_id': chat_id}, {'chat_id': chat_id, 'state': state}, upsert=True)

    def get_state(self, chat_id):
        state_table = self.db['user_state']
        return state_table.find_one({'chat_id': chat_id})['state']

    def log_migraine(self, chat_id, request):
        current_log_table = self.db['current_log']
        current_log_table.update({'chat_id': chat_id}, request, upsert=True)

    def get_log(self, chat_id):
        current_log_table = self.db['current_log']
        return current_log_table.find_one({'chat_id': chat_id})

    def save_log(self, chat_id):
        current_log_table = self.db['current_log']
        migraine_logs = self.db['migraine_logs']
        current_log = current_log_table.find_one({'chat_id': chat_id})
        current_log_table.delete_one({'chat_id': chat_id})
        migraine_logs.insert(current_log)

    def save_stats_csv(self, chat_id):
        migraine_logs = self.db['migraine_logs']
        user_logs = migraine_logs.find({'chat_id': chat_id})

        df = pd.DataFrame()
        for i, log in enumerate(user_logs):
            for key in log.keys():
                df.loc[i, key] = log[key]

        df.drop(columns=['chat_id', '_id'], inplace=True)
        df.sort_values(by='date', inplace=True)
        df.reset_index(drop=True, inplace=True)

        username = self.get_username(chat_id)
        filename = f'/tmp/{username}_logs_{date.today().strftime("%d-%m-%Y")}.csv'
        df.to_csv(filename)
        return filename
