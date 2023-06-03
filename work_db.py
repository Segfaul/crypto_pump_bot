import sqlite3
import inspect
from datetime import datetime, date, timedelta


class PumpDB:

    def __init__(self, db_root: str, logger):
        self.db_root = db_root
        self.logger = logger
        self.create_tables()

    def __str__(self):
        return f"Post database connector for {self.db_root} root."

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PumpDB, cls).__new__(cls)
        return cls.instance

    '''             
    ----------------------------------------------
                    Client logic             
    ----------------------------------------------
    '''

    def create_tables(self) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')

        try:
            base.execute(
                'CREATE TABLE IF NOT EXISTS Users ('
                'id INT PRIMARY KEY, '
                'username VARCHAR(30), '
                'api_k VARCHAR(65), '
                'api_s VARCHAR(65), '
                'sub DATE, '
                'status BOOLEAN, '
                'percent REAL CHECK (percent >= 0 AND percent <= 100)'
                ')'
            )
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        self.logger.info(f"{func_name}")

        return 0

    def check_sub(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            sub = cur.execute('SELECT sub FROM users WHERE (id == ? AND sub is not NULL)', (tg_id,)).fetchone()[0]
            if sub:
                self.logger.error(f"{__name__}/{sub}")
                if datetime.strptime(sub, '%Y-%m-%d') >= datetime.now():
                    return sub.split('-')
                else:
                    return 1

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{sub}")
        return 1

    def input_user(self, tg_id: int, username: str = None) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            if username:
                cur.execute('INSERT INTO users (id, username) VALUES(?, ?)', (tg_id, username,))
            else:
                cur.execute('INSERT INTO users (id) VALUES(?)', (tg_id,))
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{tg_id}")
        return 0

    def check_user(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            res = cur.execute('SELECT EXISTS(SELECT id FROM users WHERE id == ?)', (tg_id,)).fetchone()[0]
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{tg_id}")
        return res

    def get_user(self, tg_id: int) -> list or int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            data = list(cur.execute('SELECT * FROM users WHERE id == ?', (tg_id,)).fetchone())
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{tg_id}")
        return data

    def change_user_api(self, tg_id: int, api_k: str, secret_k: str) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            cur.execute('UPDATE users SET api_k == ?, api_s == ? WHERE id == ?',
                        (f'{api_k}', f'{secret_k}', tg_id,))
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{tg_id}")
        return 0

    def reset_user(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            cur.execute('UPDATE users SET api_k == NULL, secret_k == NULL, status == NULL, percent == NULL '
                        'WHERE id == ?',
                        (tg_id,))
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{tg_id}")
        return 0

    def switch_status(self, tg_id: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()
        res = 0

        try:
            status = cur.execute('SELECT status FROM users WHERE id == ?', (tg_id,)).fetchone()[0]

            if status == 0:
                cur.execute('UPDATE users SET status == ? WHERE id == ?', (1, tg_id))
                res += 1
            else:
                cur.execute('UPDATE users SET status == ? WHERE id == ?', (0, tg_id))

            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{tg_id}")

        return res

    def resize_percent(self, tg_id: int, percent: int or float) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            cur.execute('UPDATE users SET percent == ? WHERE id == ?', (percent, tg_id,))
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{percent}||{tg_id}")

        return 0

    '''             
    ----------------------------------------------
                    Admin logic             
    ----------------------------------------------
    '''

    @property
    def get_stats(self) -> [int] or int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()
        stats: [int] = []

        try:
            stats.append(len(cur.execute('SELECT * FROM users').fetchall()))
            stats.append(len(cur.execute('SELECT * FROM users WHERE sub is not NULL').fetchall()))

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{stats}")

        return stats

    def add_sub(self, tg_id: int, np: int) -> int:
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            new_sub = date.today() + timedelta(60)
            if np == 0:
                cur.execute('UPDATE users SET sub == NULL WHERE id == ?', (tg_id,))
            elif np == 1:
                cur.execute('UPDATE users SET sub == ? WHERE id == ?',
                            (new_sub, tg_id,))
            base.commit()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{__name__}/{tg_id, new_sub}")
        return 0

    @property
    def get_last_records(self):
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()
        final = ''

        try:
            users = cur.execute('SELECT * FROM users').fetchall()
            if len(users) >= 3:
                for record in users[-3::]:
                    final += ' '.join(record) + '\n'

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        self.logger.info(f"{func_name}/{final}")
        return final

    @property
    def get_all_ready(self):
        func_name = inspect.currentframe().f_code.co_name
        base = sqlite3.connect(f'{self.db_root}')
        cur = base.cursor()

        try:
            arr_of_r = cur.execute(
                'SELECT * FROM users '
                'WHERE (status == ? AND sub is not NULL AND api_k is not NULL AND secret_k is not NULL)',
                (1,)).fetchall()

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")
            return -1

        finally:
            base.close()

        return arr_of_r
