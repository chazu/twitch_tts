import irc.bot
import pyttsx3
import requests

def message_tags_to_dict(msg):
    return {x["key"]: x["value"] for x in msg.tags}

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.last_to_speak = None
        self.tts_engine = pyttsx3.init()

        # Initialize the TTS engine
        fred_index = self.voice_names().index('Fred')
        self.tts_engine.setProperty('voice', self.voices()[fred_index].id)

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

    def voices(self):
        return self.tts_engine.getProperty('voices')

    def voice_names(self):
        return [x.name for x in self.tts_engine.getProperty('voices')]

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
            self.tts_engine.say(to_read)
            self.tts_engine.runAndWait()

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
            c.privmsg(self.channel, str(self.voice_names()))
        elif cmd == "setvoice":
            voice_name = e.arguments[0].split(' ')[-1]
            try:
                index = self.voice_names().index(voice_name)
                self.tts_engine.setProperty('voice', self.voices()[index].id)
                self.tts_engine.say(f"Voice is now {voice_name}")
                self.tts_engine.runAndWait()
            except ValueError:
                print(voice_name)
                c.privmsg(self.channel, "That voice isn't available...")

        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)
