from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os
import sys

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = SlackClient(slack_bot_token)

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
    # Ensure bot does not respond to it's own messages      Bot User ID = U011AJZNY6M
    if message.get("subtype") is None and message["user"]!="U011AJZNY6M":
        channel = message["channel"]
        text=message.get('text')
        text=text.lower()
        jiraTicket=False
        response=""

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

# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(port=3000)
