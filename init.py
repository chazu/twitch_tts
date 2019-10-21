import os
import sys

from dotenv import load_dotenv
from twitch_tts.twitch_bot import TwitchBot

load_dotenv()

def main():
    username  = "gossamer_socks"
    client_id = os.getenv("TWITCH_CLIENT_ID")
    token     = os.getenv("TWITCH_TOKEN")
    channel   = os.getenv("CHANNEL")

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
