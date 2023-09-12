import slack
import os
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import string

# send a message in the channel
load_dotenv(dotenv_path = os.getcwd() + "/src/.env")
client = slack.WebClient(token = os.environ['SLACK_TOKEN'])
client.chat_postMessage(
    channel = '#myorg-slackbot',
    text = 'Welcome to the channel!'
)

# handling events
app = Flask(__name__) #__name__ represents name of file
# SlackEventAdapter helps to manage events triggered by slack API
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'],
    '/slack/events', # the route where slack events get sent to
    app) # the webserver where the events are sent
BOT_ID = client.api_call("auth.test")['user_id'] # get user id of slackbot
# method to handle message sent from slack API
message_counts = {}
welcome_messages = {}
WORDS_TO_CHECK = ['hmm','ok','nooo']

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event',{}) # look for key 'event' in data/message/payload sent
    channel_id = event.get('channel') # channel ID of message
    user_id = event.get('user') # user ID of message
    text = event.get('text')
    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1
        client.chat_postMessage(channel = channel_id, text = text) # whatever message is sent on slack, returns back same message in channel
        if text.lower() == 'start': # everytime a user sends start in the channel, a welcome message is sent
            send_welcome_message(f'@{user_id}',user_id)
        elif check_if_word(text):
            ts = event.get('ts') # no two message are sent at the same time because it also records nano seconds
            client.chat_postMessage(channel = channel_id, thread_ts = ts, text = 'That is unacceptable!')

# slash command example
@app.route('/message-count',methods=['POST']) # allow for post requests to be sent at this endpoint
def message_count():
    data = request.form # collect the information sent via POST request
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id,0)
    client.chat_postMessage(channel = channel_id, text=f"Message: {message_count}")
    return Response(), 200

# markdown messages & emojis
class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to this awesome channel! \n\n'
                '*Get started by completing the tasks!*'
            )
        }
    }
    DIVIDER = {'type': 'divider'}
    def __init__(self,channel,user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:' # text within :: defines emoji
        self.timestamp = ''
        self.completed = False
    
    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'
        text = f'{checkmark} *React to this message!*'
        return {'type': 'section', 'text': {'type':'mrkdwn','text':text}}
    
def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}
    if user in welcome_messages[channel]:
        return            
    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']
    welcome_messages[channel][user] = welcome

# handling reaction to messages
@slack_event_adapter.on('reaction_added')
def reaction(payload):
    event = payload.get('event',{})
    channel_id = event.get('item',{}).get('channel')
    user_id = event.get('user')
    if f'@{user_id}' not in welcome_messages:
        # checking if the reaction is in the channel that wasn't where the welcome message was sent then we are not updating the welcome message
        return
    welcome = welcome_messages[f'@{user_id}'][user_id]
    welcome.completed = True
    welcome.channel = channel_id
    message = welcome.get_message() # this will have the check mark instead of the box
    updated_message = client.chat_update(**message)
    welcome.timestamp = updated_message['ts']

# replying to messages
def check_if_word(message):
    msg = message.lower()
    # remove all punctuation marks from the string
    msg = msg.translate(str.maketrans('','',string.punctuation))
    return any(word in msg for word in WORDS_TO_CHECK)

if __name__ == "__main__":
    app.run(debug = True)
