import requests

from twitch_tts.commands.base import Command

class TitleCommand(Command):

    def execute(self, context, event):
        url = 'https://api.twitch.tv/kraken/channels/' + context.channel_id
        headers = {'Client-ID': context.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        context.connection.privmsg(context.channel, r['display_name'] + ' channel title is currently ' + r['status'])
