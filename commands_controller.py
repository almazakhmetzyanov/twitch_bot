# -*- coding: utf-8 -*-
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandsController:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.cursor = self.conn.cursor()

    def get_command_answer(self, command_name):
        sql = """select answer from commands where command == \"{}\"""".format(command_name)
        return self.cursor.execute(sql).fetchone()

    def create_command(self, command_name, command_answer):
        sql = """INSERT INTO commands VALUES (\"{}\", \"{}\")""".format(command_name, command_answer)
        if self.get_command_answer(command_name):
            return 'Команда {} уже существует'.format(command_name)
        else:
            self.cursor.execute(sql)
            self.conn.commit()
            return 'Команда {} успешно создана'.format(command_name)

    def delete_command(self, command_name):
        sql = """delete from commands where command == \"{}\"""".format(command_name)
        if self.get_command_answer(command_name):
            self.cursor.execute(sql)
            self.conn.commit()
            return 'Команда {} удалена'.format(command_name)
        else:
            return 'Команды {} нет в базе'.format(command_name)

    def update_command(self, command_name, new_value):
        sql = """update commands set answer = \"{}\" where command = \"{}\"""".format(new_value, command_name)
        if self.get_command_answer(command_name):
            self.cursor.execute(sql)
            self.conn.commit()
            return 'Команда успешно обновлена'

    def execute_command(self, command_name):
        answer = self.get_command_answer(command_name)
        if answer:
            return answer[0]
        else:
            return None

    def get_all_cmds(self):
        sql = """select * from commands"""
        accounts = self.cursor.execute(sql).fetchall()
        report_list = []
        place = 1
        for i in accounts:
            report_list.append("!{} ".format(i[0]))
            place += 1
            s = ""
            report_str = s.join(report_list)
            return report_str


if __name__ == "__main__":
    print(CommandsController().execute_command(command_name=''))
