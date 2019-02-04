# -*- coding: utf-8 -*-
import random
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountsController:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.cursor = self.conn.cursor()

    def get_accounts(self):
        sql = """SELECT account_name FROM accounts"""
        # from tuple to list
        accounts = list(sum(self.cursor.execute(sql).fetchall(), ()))
        return accounts

    def append_account(self, account_name):
        accounts = self.get_accounts()
        if account_name in accounts:
            return False
        sql = """INSERT INTO accounts VALUES (\"{}\", 0)""".format(account_name)
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def append_win_count(self, account_name):
        sql = """update accounts
                 set win_count = (select win_count
                 from accounts
                 where account_name = \"{}\") + 1
                 where account_name = \"{}\"""".format(account_name, account_name)
        self.cursor.execute(sql)
        self.conn.commit()

    def get_win_count(self, account_name):
        sql = """select win_count from accounts where account_name = \"{}\"""".format(account_name)
        win_count = self.cursor.execute(sql).fetchone()
        return win_count[0]

    def get_top5(self):
        sql = """select * from accounts order by win_count desc limit 5"""
        accounts = self.cursor.execute(sql).fetchall()
        report_list = []
        place = 1
        for i in accounts:
            report_list.append("{} - {}: {}. ".format(place, i[0], i[1]))
            place += 1
        s = ""
        report_str = s.join(report_list)
        return report_str

    def get_account_duel_result(self, duel_initiator, duel_enemy):
        accounts = self.get_accounts()
        if duel_initiator in accounts and duel_enemy in accounts:
            random_pull = [duel_initiator, duel_enemy]
            duel_loser = random_pull[random.randint(0, 1)]
            if duel_loser == duel_initiator:
                self.append_win_count(duel_enemy)
            elif duel_loser == duel_enemy:
                self.append_win_count(duel_initiator)
            return duel_loser
        else:
            return False


if __name__ == "__main__":
    AccountsController().append_account('ghjfghjfgjhfg')
