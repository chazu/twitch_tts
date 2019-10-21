import os
import sys

from dotenv import load_dotenv
import irc.bot
import pyttsx3
import requests

load_dotenv()

def message_tags_to_dict(msg):
    return {x["key"]: x["value"] for x in msg.tags}


# GLOBAL STATE IS THE BEST!!!

engine = pyttsx3.init()
voices = engine.getProperty('voices')
voice_names = [voice.name for voice in voices]
fred_index = voice_names.index('Fred')
engine.setProperty('voice', voices[fred_index].id)


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.last_to_speak = None

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)


    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        tags = message_tags_to_dict(e)

        print(tags)

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        else:
            display_name = e.tags[3]['value']

            to_read = ""

            if self.last_to_speak != display_name:
                to_read += f"{display_name} says "

            to_read += f"{e.arguments[0]}"
            print("===")
            print(to_read)
            print("===")
            engine.say(to_read)
            engine.runAndWait()

            self.last_to_speak = display_name

    def do_command(self, e, cmd):
        c = self.connection

        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])
        elif cmd == "voices":
            voice_names = [x.name for x in engine.getProperty('voices')]
            c.privmsg(self.channel, str(voice_names))
            # print(engine.getProperty('voices'))
        elif cmd == "setvoice":
            voices = engine.getProperty('voices')
            voice_names = [voice.name for voice in voices]
            voice_name = e.arguments[0].split(' ')[-1]
            try:
                index = voice_names.index(voice_name)
                engine.setProperty('voice', voices[index].id)
                engine.say(f"Voice is now {voice_name}")
                engine.runAndWait()
            except ValueError:
                print(voice_name)
                c.privmsg(self.channel, "That voice isn't available...")

        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():
    # if len(sys.argv) != 5:
    #     print("Usage: twitchbot <username> <client id> <token> <channel>")
    #     sys.exit(1)

    username  = "gossamer_socks"
    client_id = os.getenv("TWITCH_CLIENT_ID")
    token     = os.getenv("TWITCH_TOKEN")
    channel   = os.getenv("CHANNEL")

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
