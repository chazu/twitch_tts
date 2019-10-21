import os
import sys

from dotenv import load_dotenv
from twitch_tts.twitch_bot import TwitchBot
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

    bot.start()

if __name__ == "__main__":
    main()
