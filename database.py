import pymongo
import pandas as pd
from datetime import date
from config.config import mongo_host


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(mongo_host)
        self.db = self.client['migraine_bot']
        self.users_table = self.db['users']
        self.state_table = self.db['user_state']
        self.current_log_table = self.db['current_log']
        self.migraine_logs = self.db['migraine_logs']

    def insert_user(self, chat_id, username):
        self.users_table.update({'chat_id': chat_id}, {'chat_id': chat_id, 'username': username}, upsert=True)

    def get_username(self, chat_id):
        return self.users_table.find_one({'chat_id': chat_id})['username']

    def set_state(self, chat_id, state):
        self.state_table.update({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'state': state}}, upsert=True)

    def get_state(self, chat_id):
        return self.state_table.find_one({'chat_id': chat_id})['state']

    def set_step(self, chat_id, step):
        self.state_table.update({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'step': step}}, upsert=True)

    def get_step(self, chat_id):
        return self.state_table.find_one({'chat_id': chat_id})['step']

    def log_migraine(self, chat_id, request):
        self.current_log_table.update({'chat_id': chat_id}, request, upsert=True)

    def get_log(self, chat_id):
        return self.current_log_table.find_one({'chat_id': chat_id})

    def delete_current_log(self, chat_id):
        self.current_log_table.delete_one({'chat_id': chat_id})

    def save_log(self, chat_id):
        current_log = self.current_log_table.find_one({'chat_id': chat_id})
        self.current_log_table.delete_one({'chat_id': chat_id})
        self.migraine_logs.update({'_id': current_log['_id']}, current_log, upsert=True)

    def fetch_last_log(self, chat_id):
        request = self.migraine_logs.find_one({'chat_id': chat_id}, sort=[('_id', pymongo.DESCENDING)])
        self.log_migraine(chat_id, request)
        return request

    def save_stats_csv(self, chat_id):
        user_logs = self.migraine_logs.find({'chat_id': chat_id})

        df = pd.DataFrame()
        for i, log in enumerate(user_logs):
            for key in log.keys():
                df.loc[i, key] = log[key]

        df.drop(columns=['chat_id', '_id'], inplace=True)
        df.sort_values(by='date', inplace=True)
        df['date'] = df['date'].dt.strftime('%d-%m-%y')
        df.reset_index(drop=True, inplace=True)

        username = self.get_username(chat_id)
        filename = f'/tmp/{username}_logs_{date.today().strftime("%d-%m-%Y")}.csv'
        df.to_csv(filename)
        return filename

    def get_stats_month(self, chat_id, month, year):
        user_logs = self.migraine_logs.find({
            "$expr": {
                "$and": [
                    {'chat_id': chat_id},
                    {"$eq": [{"$year": "$date"}, year]},
                    {"$eq": [{"$month": "$date"}, month]}
                ]
            }
        })
        return user_logs


