from twitch_tts.commands.base import Command

class SetVoiceCommand(Command):

    def execute(self, context, event):
        voice_name = event.arguments[0].split(' ')[-1]
        try:
            index = context.voice_names().index(voice_name)
            context.tts_engine.setProperty('voice', context.voices()[index].id)
            context.tts_engine.say(f"Voice is now {voice_name}")
            context.tts_engine.runAndWait()
        except ValueError:
            print(voice_name)
            context.connection.privmsg(context.channel, "That voice isn't available...")
