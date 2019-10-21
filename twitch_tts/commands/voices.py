from twitch_tts.commands.base import Command

class VoicesCommand(Command):

    def execute(self, context, event):
            context.connection.privmsg(context.channel, str(context.voice_names()))
