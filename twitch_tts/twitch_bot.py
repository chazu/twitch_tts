# Python Imports
import random

# Third Party Imports
import irc.bot
import pyttsx3
import requests

# Own imports
from .voice_rankings import VOICE_RANKINGS

VOICE_QUALITY = {
    "normal": ["Fred"],
    "acceptable": ["Nora"],
    "crappy": ["Zuzana"]
}


def message_tags_to_dict(msg):
    """Return the message tags as a dictionary"""
    return {x["key"]: x["value"] for x in msg.tags}


class TwitchBot(irc.bot.SingleServerIRCBot):
    """The bot"""

    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.last_to_speak = None
        self.tts_engine = pyttsx3.init()
        self.command_registry = {}

        self.voice_registry = {}

        # Initialize the TTS engine
        default_voice_index = self.voice_names().index('Fred')
        self.default_voice = self.voices()[default_voice_index]
        self._set_voice(self.default_voice)

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self,
                                            [(server, port, 'oauth:'+token)],
                                            username,
                                            username)

    def get_voice(self, voice_name):
        """Given a voice name, return that voice"""
        index_of_voice = self.voice_names().index(voice_name)
        return self.voices()[index_of_voice]

    def voices(self):
        return self.tts_engine.getProperty('voices')

    def register_command(self, trigger, command_instance):
        self.command_registry[trigger] = command_instance

    def voice_names(self):
        return [x.name for x in self.tts_engine.getProperty('voices')]

    def on_welcome(self, c, event):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, event):
        """Handle a public message"""

        tags = message_tags_to_dict(event)
        print(tags)

        # If a chat message starts with an exclamation point, try to run it as a command
        if event.arguments[0][:1] == '!':
            cmd = event.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(event, cmd)
        else:
            display_name = event.tags[3]['value']

            if self.last_to_speak != display_name:
                self._set_voice(self.default_voice)
                name_to_read = f"{display_name} says "
                self.tts_engine.say(name_to_read)

            user_voice = self._voice_for_user(display_name)
            user_words = event.arguments[0]

            print(user_words)

            self._set_voice(user_voice)
            self._say(user_words)
            self.last_to_speak = display_name

    def _say(self, words):
        self.tts_engine.say(words)
        self.tts_engine.runAndWait()

    def _set_voice(self, voice):
        self.tts_engine.setProperty('voice', voice.id)

    def _voice_for_user(self, user_name):
        print(self.voice_registry)
        try:
            voice_name_for_user = self.voice_registry[user_name]
            return self.get_voice(voice_name_for_user)
        except KeyError:
            voice_for_user = self._pick_unused_voice()

            self.voice_registry[user_name] = voice_for_user.name
            return voice_for_user

    def _pick_unused_voice(self):
        """Pick an unused voice."""
        return random.choice(self._unused_voices())

    def _unused_voices(self):
        used_voice_names = list(self.voice_registry.values())
        return [voice for voice in self.voices()
                if voice.name in VOICE_RANKINGS["good"]]

    def do_command(self, event, cmd):
        """Do a command"""
        try:
            command_instance = self.command_registry[cmd]
            command_instance.execute(self, event)
        except KeyError:
            self.connection.privmsg(self.channel, f"Invalid Command {cmd}")
