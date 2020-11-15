import pymongo
import pandas as pd
from datetime import date, datetime
from config.config import mongo_host, mongo_pwd, mongo_admin
import numpy as np
import locale
import logging
from config.messages import default_name

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
        self.user_meds = self.db['user_meds']

    def insert_user(self, chat_id, username):
        try:
            self.users_table.update_one({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'username': username}},
                                        upsert=True)
            logger_db.debug(f'{chat_id}: insert new user {username}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "users_table" - update_one username {username}')
            raise e

    def exists_user(self, chat_id):
        try:
            return self.users_table.find({'chat_id': chat_id}).count()
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "users_table" - find/count')
            raise e

    def get_username(self, chat_id):
        try:
            user = self.users_table.find_one({'chat_id': chat_id})
            if user.get('username') is None:
                return None
            return self.users_table.find_one({'chat_id': chat_id})['username']
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "users_table" - find_one')
            raise e

    def get_lang(self, chat_id, return_none=False):
        try:
            if self.exists_user(chat_id):
                user = self.users_table.find_one({'chat_id': chat_id})
            else:
                return None
            if user.get('lang') is None:
                if return_none:
                    return None
                self.users_table.update_one({'chat_id': chat_id}, {"$set": {'chat_id': chat_id, 'lang': 'en'}})
                logger_db.debug(f'{chat_id}: set lang en')
                return 'en'
            else:
                return user['lang']
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "users_table" - find_one, update')
            raise e

    def set_lang(self, chat_id, lang):
        try:
            if lang != 'ru':
                lang = 'en'
            self.users_table.update_one({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'lang': lang}}, upsert=True)
            logger_db.debug(f'{chat_id}: set lang {lang}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "users_table" - update')
            raise e

    def set_state(self, chat_id, state):
        try:
            self.state_table.update_one({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'state': state}},
                                        upsert=True)
            logger_db.debug(f'{chat_id}: set state {state}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "state_table" - update_one state {state}')
            raise e

    def get_state(self, chat_id):
        try:
            return self.state_table.find_one({'chat_id': chat_id})['state']
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "state_table" - find_one')
            raise e

    def set_step(self, chat_id, step):
        try:
            self.state_table.update_one({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'step': step}}, upsert=True)
            logger_db.debug(f'{chat_id}: set step {step}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "state_table" - update_one step {step}')
            raise e

    def get_step(self, chat_id):
        try:
            return self.state_table.find_one({'chat_id': chat_id})['step']
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "state_table" - find_one')
            raise e

    def log_migraine(self, chat_id, migraine_data: dict, append=False):
        try:
            if append:
                for field_key in migraine_data.keys():
                    current_log_entry = self.current_log_table.find_one({'chat_id': chat_id})
                    if current_log_entry.get(field_key) is None or current_log_entry[field_key] == "":
                        self.current_log_table.update_one({'chat_id': chat_id},
                                                          {"$set": {field_key: migraine_data[field_key]}}, upsert=True)
                    else:
                        self.current_log_table.update_one({'chat_id': chat_id},
                                                          [{"$set": {field_key: {"$concat":
                                                                                     ["$" + field_key, ", ",
                                                                                      migraine_data[field_key]]}}}])
                    logger_db.debug(f'{chat_id}: appended to {field_key} in "current log" collection {migraine_data}')
            else:
                self.current_log_table.update_one({'chat_id': chat_id}, {"$set": migraine_data}, upsert=True)
                logger_db.debug(f'{chat_id}: logged migraine details to "current log" collection {migraine_data}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "current_log" - update_one {migraine_data}')
            raise e

    def get_current_log(self, chat_id):
        try:
            return self.current_log_table.find_one({'chat_id': chat_id})
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "current_log" - find_one')
            raise e

    def delete_current_log(self, chat_id):
        try:
            self.current_log_table.delete_many({'chat_id': chat_id})
            logger_db.debug(f'{chat_id}: deleted current log ')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "current_log" - delete_many')
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
            logger_db.error(f'{chat_id}: "current_log" - find/delete_one (num {num})')
            raise e

    def save_log(self, chat_id):
        try:
            current_log = self.current_log_table.find_one({'chat_id': chat_id})
            logger_db.debug(f'{chat_id}: fetched migraine log from "current_log" collection '
                            f'{current_log}')

            self.current_log_table.delete_one({'chat_id': chat_id})
            current_log['last_modified'] = datetime.today()
            self.migraine_logs.replace_one({'_id': current_log['_id']}, current_log, upsert=True)

            logger_db.debug(f'{chat_id}: saved migraine log to "migraine_logs" collection '
                            f'{list(current_log)}')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "current_log" - find_one, delete_one, "migraine_logs" - update')
            raise e

    def fetch_last_log(self, chat_id):
        try:
            request = self.migraine_logs.find_one({'chat_id': chat_id}, sort=[('last_modified', pymongo.DESCENDING)])
            self.log_migraine(chat_id, request)
            return request
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "migraine_logs" - find_one, self.log_migraine')
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
                logger_db.error(f'{chat_id}: dataframe key error {df.columns} '
                                   f'(should be chat_id, _id, last_modified, date), {df.info()}')

            username = self.get_username(chat_id)
            if username == default_name['en'] or username == default_name['ru'] or username is None:
                username = 'migraine'
            filename = f'/tmp/{username}_logs_{date.today().strftime("%d-%m-%Y")}.csv'
            df.to_csv(filename)
            return filename
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "migraine_logs" - find')
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
            logger_db.error(f'{chat_id}: "migraine_logs" - find ({month, year})')
            raise e

    def get_last_dates(self, chat_id, n):
        try:
            user_logs = self.migraine_logs.find({'chat_id': chat_id}).distinct('date')
            dates = np.unique([date(dt.year, dt.month, dt.day) for dt in user_logs])
            logger_db.debug(f'{chat_id}: get last {n} logs - {dates}')
            lang = self.get_lang(chat_id)
            if lang == 'ru':
                locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
            else:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            return [date.strftime(dt, '%d %b %Y') for dt in dates[:-1 - n:-1]]
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "migraine_logs" - find, np.unique, strftime ({n})')
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
            logger_db.error(f'{chat_id}: "migraine_logs" - find ({attack_date}), "current_log" - insert_many')
            raise e

    def add_med(self, chat_id, med):
        try:
            self.user_meds.update_one({'chat_id': chat_id}, {"$addToSet": {'meds': med}}, upsert=True)
            logger_db.debug(f'{chat_id}: added {med} in "user_meds" ')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "user_meds" - update_one med: {med}')
            raise e

    def get_meds(self, chat_id):
        try:
            meds = self.user_meds.find_one({'chat_id': chat_id})
            logger_db.debug(f'{chat_id}: retrieve {meds} in "user_meds" ')
            if meds is None:
                return []
            if meds.get('meds') is None:
                return []
            return meds['meds']

        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "user_meds" - find')
            raise e

    def remove_med(self, chat_id, med):
        try:
            self.user_meds.update_one({'chat_id': chat_id}, {"$pull": {'meds': med}})
            logger_db.debug(f'{chat_id}: removed {med} from "user_meds"')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "user_meds" - update, pull med: {med}')
            raise e

    def set_meds_msg_id(self, chat_id, msg_id):
        try:
            self.user_meds.update_one({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'msg_id': msg_id}},
                                      upsert=True)
            logger_db.debug(f'{chat_id}: added {msg_id} in "user_meds" ')
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "user_meds" - update_one msg_id: {msg_id}')
            raise e

    def get_meds_msg_id(self, chat_id):
        try:
            user_meds_row = self.user_meds.find_one({'chat_id': chat_id})
            if user_meds_row is None:
                logger_db.debug(f'{chat_id}: no user in "user_meds" ')
                return None
            if user_meds_row.get('msg_id') is None:
                logger_db.debug(f'{chat_id}: no msg_id in "user_meds" ')
                return None
            msg_id = user_meds_row['msg_id']
            logger_db.debug(f'{chat_id}: retrieve msg_id {msg_id} from "user_meds" ')
            return msg_id
        except Exception as e:
            logger_db.exception(e)
            logger_db.error(f'{chat_id}: "user_meds" - find_one')
            raise e
