# -*- coding: utf-8 -*-
import config
import requests

corr_mush_channel_id = 155850884
segall_channel_id = 35856714


class TwitchClient:
    def __init__(self):
        self.oauth_token = config.TWITCH_OAUTH_TOKEN
        self.client_id = config.CLIENT_ID
        self.url = 'https://api.twitch.tv/kraken/'
        self.headers = {"Client-ID": self.client_id,
                        "Accept": "application/vnd.twitchtv.v5+json",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": "OAuth {}".format(self.oauth_token)}

    def change_game(self, game):
        data = 'channel[game]={}'.format(game)
        resp = requests.put(url="{}channels/{}".format(self.url, segall_channel_id), data=data, headers=self.headers)
        if resp.status_code == 200:
            return True
        else:
            return False


if __name__ == "__main__":
    TwitchClient().change_game()
