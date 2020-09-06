import pymongo
import pandas as pd
from datetime import date, datetime
from config.config import mongo_host
import numpy as np


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

    def get_current_log(self, chat_id):
        return self.current_log_table.find_one({'chat_id': chat_id})

    def delete_current_log(self, chat_id):
        self.current_log_table.delete_many({'chat_id': chat_id})

    def keep_one_log(self, chat_id, num):
        current_logs = self.current_log_table.find({'chat_id': chat_id})
        if (num >= current_logs.count()) or (num < 0):
            return -1
        for i, entry in enumerate(current_logs):
            if i != num:
                self.current_log_table.delete_one(entry)
        return 0

    def save_log(self, chat_id):
        current_log = self.current_log_table.find_one({'chat_id': chat_id})
        self.current_log_table.delete_one({'chat_id': chat_id})
        current_log['last_modified'] = datetime.today()
        self.migraine_logs.update({'_id': current_log['_id']}, current_log, upsert=True)

    def fetch_last_log(self, chat_id):
        request = self.migraine_logs.find_one({'chat_id': chat_id}, sort=[('last_modified', pymongo.DESCENDING)])
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

    def get_last_dates(self, chat_id, n):
        user_logs = self.migraine_logs.find({'chat_id': chat_id}).distinct('date')
        dates = np.unique([date(dt.year, dt.month, dt.day) for dt in user_logs])
        return [date.strftime(dt, '%d %b %Y') for dt in dates[:-1 - n:-1]]

    def get_log(self, chat_id, date):
        user_logs = list(self.migraine_logs.find({
            "$expr": {
                "$and": [
                    {'chat_id': chat_id},
                    {"$eq": [{"$year": "$date"}, date.year]},
                    {"$eq": [{"$month": "$date"}, date.month]},
                    {"$eq": [{"$dayOfMonth": "$date"}, date.day]}
                ]
            }
        }, sort=[('date', pymongo.ASCENDING)]))
        if len(user_logs) != 0:
            self.current_log_table.insert_many(user_logs)
        return user_logs
