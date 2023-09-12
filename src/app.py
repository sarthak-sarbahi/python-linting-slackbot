import slack
import os
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import string
import re
from io import StringIO
from pylint.lint import Run
from pylint.reporters.text import TextReporter
import subprocess
import time

app = Flask(__name__)
load_dotenv(dotenv_path = os.getcwd() + "/src/.env")
client = slack.WebClient(token = os.environ['SLACK_TOKEN'])
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'],
    '/slack/events',
    app)

BOT_ID = client.api_call("auth.test")['user_id']
client_msg_id_list = list()

@slack_event_adapter.on('message')
def message(payload):
    """
    This function replies to the user in a thread
    """
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != None and BOT_ID != user_id:
        ts = event.get('ts')
        client_msg_id = event.get('client_msg_id')
        if client_msg_id not in client_msg_id_list and 'lint_file' not in text:
            if '```' in text:
                if extractCode(text):
                    response = lintCode()
                    reply = '```' + '\n'.join(response) + '```'
                    if 'lint_file.py' not in reply:
                        client.chat_postMessage(channel = channel_id, thread_ts = ts, text = reply, mrkdwn=True)
                        if os.path.exists("lint_file.py"): 
                            os.remove("lint_file.py")
                else:
                    client.chat_postMessage(channel = channel_id, thread_ts = ts, text = "No python code available to parse")
            client_msg_id_list.append(client_msg_id)

def extractCode(text):
    """
    This function checks if code snippet is present as part of message
    If it is present then extract the message in a .py file
    """
    if '``````' not in text:
        result = re.search(r'```(.*?)```', text, re.DOTALL)
        if result:
            code_content = result.group(1).strip()
            with open("lint_file.py", "w") as file:
                file.write(code_content)
            return True
        else:
            return False
    else:
        return False
    
def lintCode():
    """
    This function lints the python code
    """
    command = ["python3","-m","pylint","lint_file.py","--score=n","--msg-template=Line {line} : {msg}"] # split the command into a list of arguments
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True) # run the command and capture the output
    output = result.stdout
    filtered_output = [line for line in output.split("\n") if not line.startswith("************* Module")]
    return filtered_output

if __name__ == "__main__":
    app.run(debug = True)