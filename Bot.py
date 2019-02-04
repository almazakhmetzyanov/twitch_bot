# -*- coding: utf-8 -*-
import random

import irc.bot
import requests
import config
import logging
from accounts_controller import AccountsController
from twitch_client import TwitchClient
from commands_controller import CommandsController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
moders_list = ['papakarloff', 'segall', 'strangebreakers', 'wave6lol', 'bayer1by']
moders_white_list = ['corruptedmushroom', 'segall', 'strangebreakers']


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.accounts_controller = AccountsController()
        self.commands_controller = CommandsController()
        self.twitch_client = TwitchClient()
        self.is_duel_on = False

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']
        logger.info(self.channel_id)

        # Create IRC bot connection
        server = 'irc.twitch.tv'
        port = 6667
        logger.info('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + token)], username, username)

    def on_welcome(self, c, e):
        logger.info('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            receiver_name = e.tags[2]['value'].lower()
            cmd = e.arguments[0].split(' ')[0][1:]
            logger.info('Received command: {} from: {}'.format(cmd, receiver_name))
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection
        receiver_name = e.tags[2]['value'].lower()
        # to add new command add if cmd.startswith('command'):

    # TODO: Need to move all commands to another place
        # register to duels
        if cmd.startswith('reg'):
            if not self.is_duel_on:
                return
            appended = self.accounts_controller.append_account(account_name=receiver_name)
            if not appended:
                return
            c.privmsg(self.channel, text='{} зареган EZ !duel для инфы по дуэлям]'.format(receiver_name))

        # get duel stats
        if cmd.startswith('stats_duel'):
            accounts = self.accounts_controller.get_accounts()
            if receiver_name in accounts:
                win_count = self.accounts_controller.get_win_count(receiver_name)
                c.privmsg(self.channel, text='{} Количество побед: {}'.format(receiver_name, win_count))

        # get top 5 duelists
        if cmd.startswith('best_duelists'):
            if receiver_name not in moders_white_list:
                return
            report = self.accounts_controller.get_top5()
            c.privmsg(self.channel, text=str(report))

        # start duel
        if cmd.startswith('duel'):
            if not self.is_duel_on:
                return
            accounts = self.accounts_controller.get_accounts()
            enemy_name = e.arguments[0].replace('!duel ', '').lower()
            if receiver_name in moders_list:
                c.privmsg(self.channel, text='{} умный самый? Дисреспект за абуз'.format(receiver_name))
                return
            if enemy_name == '!duel':
                c.privmsg(self.channel, text='{} !duel [имя зереганного челика]'.format(receiver_name))
                logger.info('started duel: {} vs {}'.format(receiver_name, enemy_name))
                return
            elif enemy_name not in accounts:
                c.privmsg(self.channel, text='{} твой чел не зареган'.format(receiver_name))
                return
            elif receiver_name not in accounts:
                c.privmsg(self.channel, text='{} зарегайся !reg'.format(receiver_name))
                return
            loser = self.accounts_controller.get_account_duel_result(receiver_name, enemy_name)
            if not loser:
                logger.error('duel was failed')
                return
            c.privmsg(self.channel, text='/timeout {} {}'.format(loser, random.randint(1, 600)))
            logger.info('loser is {}'.format(loser))

        # turn on duels
        if cmd.startswith('turn_off_duel'):
            if receiver_name not in moders_white_list:
                return
            self.is_duel_on = False
            c.privmsg(self.channel, text='Дуэли вырублены, мечи в ножны!')

        # turn off duels
        if cmd.startswith('turn_on_duel'):
            if receiver_name not in moders_white_list:
                return
            self.is_duel_on = True
            c.privmsg(self.channel, text='SMOrc Дуэли активированы !reg для реги !duel для сражений SMOrc')

        # change game
        if cmd.startswith('change_game'):
            if receiver_name not in moders_white_list:
                return
            game = e.arguments[0].replace('!{} '.format(cmd), '')
            is_game_changed = self.twitch_client.change_game(game=game)
            if is_game_changed:
                c.privmsg(self.channel, text='Игра сменена на {}'.format(game))
            else:
                c.privmsg(self.channel, text='чот не получилось игру установить сори FeelsBadMan')

        if cmd.startswith('ебануть_команду'):
            if receiver_name not in moders_white_list:
                return
            new_command_list = str(e.arguments[0]).split(' ')
            print(new_command_list)
            print(len(new_command_list))
            if len(new_command_list) != 3:
                c.privmsg(self.channel, text='Дурачок, команда подана неправильно. Образец !ебануть_команду имя_команды ответ_ответ вместо пробела _')
                return
            command_name = new_command_list[1]
            command_answer = str(new_command_list[2]).replace("_", " ")
            c.privmsg(self.channel, text=self.commands_controller.create_command(command_name=command_name, command_answer=command_answer))

        if cmd.startswith('удали_команду'):
            if receiver_name not in moders_white_list:
                return
            command = str(e.arguments[0]).split(' ')[1]
            c.privmsg(self.channel, text=self.commands_controller.delete_command(command_name=command))

        if cmd.startswith('обнови_команду'):
            if receiver_name not in moders_white_list:
                return
            new_command_list = str(e.arguments[0]).split(' ')
            if len(new_command_list) != 3:
                c.privmsg(self.channel,
                          text='Дурачок, команда подана неправильно. Образец !обнови_команду имя_команды новое_значение вместо пробела _')
                return
            command_name = new_command_list[1]
            command_answer = str(new_command_list[2]).replace("_", " ")
            c.privmsg(self.channel, text=self.commands_controller.update_command(command_name=command_name, new_value=command_answer))

        if cmd.startswith('получить_команды'):
            if receiver_name not in moders_white_list:
                return
            c.privmsg(self.channel, text=self.commands_controller.get_all_cmds())

        if cmd:
            msg = self.commands_controller.execute_command(cmd)
            if msg:
                c.privmsg(self.channel, text=msg)


def main(username, client_id, token, channel):
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


def moderator_required(receiver_name, f):
    if receiver_name not in moders_white_list:
        return


if __name__ == "__main__":
    main(username=config.USER_NAME, client_id=config.CLIENT_ID, token=config.TOKEN,
         channel=config.CHANNEL)
