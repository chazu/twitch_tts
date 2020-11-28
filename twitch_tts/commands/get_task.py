import json
import subprocess as subp

from twitch_tts.commands.base import Command


def task_is_active(task_json: dict) -> bool:
    """Returns True if the task described by the dictionary passed in is
    current in progress.
    """
    return (True if task_json.get("start", None)
            and task_json["status"] == "pending" else False)

class GetTaskCommand(Command):

    def execute(self, context, event):
        cmd_output = subp.run("task export", shell=True,
                              capture_output=True).stdout
        tasks = json.loads(cmd_output)
        active_tasks = [task for task in tasks if task_is_active(task)]
        fred_voice_index = context.voice_names().index('Fred')

        context.tts_engine.setProperty('voice',
                                       context.voices()[fred_voice_index].id)

        if active_tasks:
            task_name = active_tasks[0]["description"]
            context.connection.privmsg(context.channel, f"Current task is: {task_name}")
            context._say(f"Current task is: {task_name}")
        else:
            context.connection.privmsg(context.channel, f"Current task is not set")
            context.tts_engine.say(f"current task is not set")
