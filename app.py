from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

import os
import sys

from flask import Flask

# Assign environment variables
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]


# Create a SlackClient for your bot to use for Web API requests
slack_client = SlackClient(slack_bot_token)



# Create Flask app
app = Flask(__name__)

# Test route for Flask app
@app.route("/")
def hello():
  return "Hello there!"

slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)


# Make URL from JIRA ticket
def devLink(message, prefix):
    nums = "1234567890"
    append = prefix
    

    currenti=message.index(prefix.lower())+len(prefix)
    while True:
        if not (currenti>=len(message)):
            if message[currenti] in nums:
                append = append+message[currenti]
                currenti+=1
            else:
                break
        else:
            break
            
    link = "https://athenacr.atlassian.net/browse/"+append
    link = "<"+link+"|"+append+"> "
    return link


# Response to new messages
@slack_events_adapter.on("message")
def handle_message(event_data):

    message = event_data["event"]
    # The text of the message is: message.get('text')
    # Ensure bot does not respond to it's own messages      Bot User ID = U011JNTNS6Q
    if message.get("subtype") is None and message["user"]!="U011JNTNS6Q":
        channel = message["channel"]
        text=message.get('text')
        text=text.lower()
        jiraTicket=False
        response=""

        print(message["user"])

        # JIRA ticket response
        # While loop handles multiple tickets in one message
        while True:
            if ('dev-' in text):
                response+=devLink(text, 'DEV-')
                jiraTicket=True
                # This line removes the first occurance of 'dev-' in the text 
                text = text[:text.index('dev-')]+text[text.index('dev-')+4:]
            elif ('pp-' in text):
                response+=devLink(text, 'PP-')
                jiraTicket=True
                text = text[:text.index('pp-')]+text[text.index('pp-')+3:]
            elif ('sc-' in text):
                response+=devLink(text, 'SC-')
                jiraTicket=True
                text = text[:text.index('sc-')]+text[text.index('sc-')+3:]
            elif ('asiaqnt-' in text):
                response+=devLink(text, 'ASIAQNT-')
                jiraTicket=True
                text = text[:text.index('asiaqnt-')]+text[text.index('asiaqnt-')+8:]
            else:
                break
        

        if jiraTicket:
            message = response
            slack_client.api_call("chat.postMessage", channel=channel, text=message,mrkdwn=False)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Start flask server on port 3000
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=3000)
