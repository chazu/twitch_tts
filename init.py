import os
import sys

from dotenv import load_dotenv
from twitch_tts.twitch_bot import TwitchBot
from twitch_tts.commands.get_task import GetTaskCommand
from twitch_tts.commands.title import TitleCommand
from twitch_tts.commands.game import GameCommand
from twitch_tts.commands.setvoice import SetVoiceCommand
from twitch_tts.commands.voices import VoicesCommand

load_dotenv()

def main():
    username  = "gossamer_socks"
    client_id = os.getenv("TWITCH_CLIENT_ID")
    token     = os.getenv("TWITCH_TOKEN")
    channel   = os.getenv("CHANNEL")

    bot = TwitchBot(username, client_id, token, channel)

    bot.register_command("game", GameCommand())
    bot.register_command("title", TitleCommand())
    bot.register_command("voices", VoicesCommand())
    bot.register_command("setvoice", SetVoiceCommand())
    bot.register_command("task", GetTaskCommand())
    bot.start()


def voices():
    username  = "gossamer_socks"
    client_id = os.getenv("TWITCH_CLIENT_ID")
    token     = os.getenv("TWITCH_TOKEN")
    channel   = os.getenv("CHANNEL")

    bot = TwitchBot(username, client_id, token, channel)

    for voice_name in bot.voice_names():

        bot._set_voice(bot.get_voice(voice_name))
        bot._say(f"This is the voice called {voice_name} do you like it")
        print(voice_name)

if __name__ == "__main__":
    main()
