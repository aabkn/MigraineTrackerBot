import pymongo
import pandas as pd
from datetime import date, datetime
from config.config import mongo_host, mongo_pwd, mongo_admin
import numpy as np
import logging

logger_db = logging.getLogger('Database')


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(mongo_host, username=mongo_admin,
                                          password=mongo_pwd)
        self.db = self.client['migraine_bot']
        self.users_table = self.db['users']
        self.state_table = self.db['user_state']
        self.current_log_table = self.db['current_log']
        self.migraine_logs = self.db['migraine_logs']

    def insert_user(self, chat_id, username):
        try:
            self.users_table.update({'chat_id': chat_id}, {'chat_id': chat_id, 'username': username}, upsert=True)
            logger_db.debug(f'{chat_id}: insert new user {username}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "users_table" - update username {username}')
            raise e

    def exists_user(self, chat_id):
        try:
            return self.users_table.find({'chat_id': chat_id}).count()
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "users_table" - find/count')
            raise e

    def get_username(self, chat_id):
        try:
            return self.users_table.find_one({'chat_id': chat_id})['username']
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "users_table" - find_one')
            raise e

    def set_state(self, chat_id, state):
        try:
            self.state_table.update({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'state': state}}, upsert=True)
            logger_db.debug(f'{chat_id}: set state {state}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "state_table" - update state {state}')
            raise e

    def get_state(self, chat_id):
        try:
            return self.state_table.find_one({'chat_id': chat_id})['state']
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "state_table" - find_one')
            raise e

    def set_step(self, chat_id, step):
        try:
            self.state_table.update({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'step': step}}, upsert=True)
            logger_db.debug(f'{chat_id}: set step {step}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "state_table" - update step {step}')
            raise e

    def get_step(self, chat_id):
        try:
            return self.state_table.find_one({'chat_id': chat_id})['step']
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "state_table" - find_one')
            raise e

    def log_migraine(self, chat_id, request):
        try:
            self.current_log_table.update({'chat_id': chat_id}, request, upsert=True)
            logger_db.debug(f'{chat_id}: logged migraine to "current log" collection {request}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "current_log" - update {request}')
            raise e

    def get_current_log(self, chat_id):
        try:
            return self.current_log_table.find_one({'chat_id': chat_id})
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "current_log" - find_one')
            raise e

    def delete_current_log(self, chat_id):
        try:
            self.current_log_table.delete_many({'chat_id': chat_id})
            logger_db.debug(f'{chat_id}: deleted current log ')
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "current_log" - delete_many')
            raise e

    def keep_one_log(self, chat_id, num):
        try:
            current_logs = self.current_log_table.find({'chat_id': chat_id})
            if (num >= current_logs.count()) or (num < 0):
                logger_db.debug(f'{chat_id}: did not delete anything since num = {num} is invalid, '
                                f'in "current_log" collection there are {current_logs.count()} documents')
                return -1
            for i, entry in enumerate(current_logs):
                if i != num:
                    self.current_log_table.delete_one(entry)
            logger_db.debug(f'{chat_id}: deleted everything in "current_log" collection except for {num}-th entry')
            return 0
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "current_log" - find/delete_one (num {num})')
            raise e

    def save_log(self, chat_id):
        try:
            current_log = self.current_log_table.find_one({'chat_id': chat_id})
            logger_db.debug(f'{chat_id}: fetched migraine log from "current_log" collection '
                            f'{current_log}')

            self.current_log_table.delete_one({'chat_id': chat_id})
            current_log['last_modified'] = datetime.today()
            self.migraine_logs.update({'_id': current_log['_id']}, current_log, upsert=True)

            logger_db.debug(f'{chat_id}: saved migraine log to "migraine_logs" collection '
                            f'{list(current_log)}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "current_log" - find_one, delete_one, "migraine_logs" - update')
            raise e

    def fetch_last_log(self, chat_id):
        try:
            request = self.migraine_logs.find_one({'chat_id': chat_id}, sort=[('last_modified', pymongo.DESCENDING)])
            self.log_migraine(chat_id, request)
            return request
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "migraine_logs" - find_one, self.log_migraine')
            raise e

    def save_stats_csv(self, chat_id):
        try:
            user_logs = self.migraine_logs.find({'chat_id': chat_id})
            if user_logs.count() == 0:
                return None

            df = pd.DataFrame()
            for i, log in enumerate(user_logs):
                for key in log.keys():
                    df.loc[i, key] = log[key]
            try:
                df.drop(columns=['chat_id', '_id', 'last_modified'], inplace=True)
                df.sort_values(by='date', inplace=True)
                df['date'] = df['date'].dt.strftime('%d-%m-%y')
                df.reset_index(drop=True, inplace=True)
            except KeyError as df_e:
                logger_db.exception(df_e)
                logger_db.critical(f'{chat_id}: dataframe key error {df.columns} '
                                   f'(should be chat_id, _id, last_modified, date), {df.info()}')

            username = self.get_username(chat_id)
            filename = f'/tmp/{username}_logs_{date.today().strftime("%d-%m-%Y")}.csv'
            df.to_csv(filename)
            return filename
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "migraine_logs" - find')
            raise e

    def get_stats_month(self, chat_id, month, year):
        try:
            user_logs = list(self.migraine_logs.find({
                "$expr": {
                    "$and": [
                        {"$eq": ["$chat_id", chat_id]},
                        {"$eq": [{"$year": "$date"}, year]},
                        {"$eq": [{"$month": "$date"}, month]}
                    ]
                }
            }))
            logger_db.debug(f'{chat_id}: find logs for one month {month, year} - {user_logs}')
            return user_logs
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "migraine_logs" - find ({month, year})')
            raise e

    def get_last_dates(self, chat_id, n):
        try:
            user_logs = self.migraine_logs.find({'chat_id': chat_id}).distinct('date')
            dates = np.unique([date(dt.year, dt.month, dt.day) for dt in user_logs])
            logger_db.debug(f'{chat_id}: get last {n} logs - {dates}')
            return [date.strftime(dt, '%d %b %Y') for dt in dates[:-1 - n:-1]]
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "migraine_logs" - find, np.unique, strftime ({n})')
            raise e

    def get_log(self, chat_id, attack_date):
        try:
            user_logs = list(self.migraine_logs.find({
                "$expr": {
                    "$and": [
                        {"$eq": ["$chat_id", chat_id]},
                        {"$eq": [{"$year": "$date"}, attack_date.year]},
                        {"$eq": [{"$month": "$date"}, attack_date.month]},
                        {"$eq": [{"$dayOfMonth": "$date"}, attack_date.day]}
                    ]
                }
            }, sort=[('date', pymongo.ASCENDING)]))
            logger_db.debug(f'{chat_id}: find logs for the date {attack_date} - {user_logs}')
            if len(user_logs) != 0:
                self.current_log_table.insert_many(user_logs)
                logger_db.debug(f'{chat_id}: insert logs in "current_log" - {user_logs}')
            return user_logs
        except Exception as e:
            logger_db.exception(e)
            logger_db.critical(f'{chat_id}: "migraine_logs" - find ({attack_date}), "current_log" - insert_many')
            raise e
