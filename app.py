# TODO Update the README

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

import os
import sys

from flask import Flask
import collections
from random import randrange

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

# Calls the Slack API method "chat.postMessage"
def postMessageToChannel(channel, response):
    slack_client.api_call("chat.postMessage", channel=channel, text=response,mrkdwn=False)

# Calls "chat.postEphemeral"
def postEphemeral(channel, user, response):
    slack_client.api_call("chat.postEphemeral", channel=channel, text=response, user=user)

# Calls API method "users.info"
def userIdtoName(user):
    call = slack_client.api_call("users.info", user=user)
    return call["user"]["profile"]["real_name"]


# Makes URL from JIRA ticket
def ticketLink(message, prefix):
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
    
    if not currenti==message.index(prefix.lower())+len(prefix):
        link = "https://athenacr.atlassian.net/browse/"+append
        link = "<"+link+"|"+append+">, "
        return link

# Responds to message with JIRA ticket links
def handleTickets(text, user, channel):
    ticketLinksIndexes = {}
    while True:
        if ('dev-' in text):
            ticketLinksIndexes[text.index('dev-')] = ticketLink(text, 'DEV-')
            # This line replaces the first occurance of 'dev-' in the text with ****
            text = text[:text.index('dev-')]+"****"+text[text.index('dev-')+4:]
        elif ('pp-' in text):
            ticketLinksIndexes[text.index('pp-')] = ticketLink(text, 'PP-')
            text = text[:text.index('pp-')]+"***"+text[text.index('pp-')+3:]
        elif ('sc-' in text):
            ticketLinksIndexes[text.index('sc-')] = ticketLink(text, 'SC-')
            text = text[:text.index('sc-')]+"***"+text[text.index('sc-')+3:]
        elif ('asiaqnt-' in text):
            ticketLinksIndexes[text.index('asiaqnt-')] = ticketLink(text, 'ASIAQNT-')
            text = text[:text.index('asiaqnt-')]+"********"+text[text.index('asiaqnt-')+8:]
        else:
            break

    orderedTicketLinks = collections.OrderedDict(sorted(ticketLinksIndexes.items()))

    if len(ticketLinksIndexes) > 0:
        response = ""
        for i in orderedTicketLinks:
            if not orderedTicketLinks[i] in response:
                response += orderedTicketLinks[i]

        # Truncate the string to cut off the final ", "
        postMessageToChannel(channel, response[:-2])


# !thanks
def thank(user, channel):
    responses=['You got it', 'Don\'t mention it', 'No worries', 'Not a problem', 'My pleasure', 'It was nothing', 'I\'m happy to help', 'Not at all', 'Sure', 'Anytime', 'You\'re welcome']
    response=responses[randrange(len(responses))]+"!"

    postMessageToChannel(channel, response)


# !help
def help(channel, args, user):
    response = "Displaying help for "
    if len(args)==0:
        response += "general commands:\n\n"
        #TODO make the help message look prettier, justify the text, etc.
        response += "!help\t\t- Display commands for talaria\n!request\t\t- Send a feature request for Talaria to Gabe\n!thank\t\t- Thank Talaria"
        
    
    else:
        # TODO add help entry for each command
        helpEntries = {
            "thank":"Use !thank or !thanks to thank Talaria."
        }
        pass

    postEphemeral(channel, user, response)

# TODO !mute

# TODO !request
def request(channel, user, text):
    # Reply to person that made the request
    if len(text) <= len("!request "):
        response = "Please provide a message for your feature request. e.g. !request Can you implement a mute feature?"
        postMessageToChannel(channel, response)
    else:
        response = "Thanks for the suggestion! It has been sent to Gabe."
        postMessageToChannel(channel, response)

        # Parse request, format it, and send it to Gabe
        text = text[len("!request"):]
        response = "New feature request from: "+userIdtoName(user)+"\n\n"+"\""+text+"\""
        postMessageToChannel("D014Y8LQREE",response)

# Handles any message starting with !, denoting a command
def handleCommands(text, user, channel):
    if text[0]=="!" and len(text) > 1:
        text = text[1:]
        args = text.split()
        cmd = args.pop(0)

        if cmd == "thank" or cmd == "thanks":
            thank(user, channel)
        
        elif cmd == "help":
            help(channel, args, user)

        elif cmd == "request":
            request(channel,user,text)



# Response to new messages
@slack_events_adapter.on("message")
def handle_message(event_data):

    message = event_data["event"]
    # The text of the message is: message["text"]
    # Ensure bot does not respond to it's own messages      Bot User ID = U011JNTNS6Q
    if message.get("subtype") is None and message["user"]!="U011JNTNS6Q":
        channel = message["channel"]
        user = message["user"]
        text=message["text"]
        text=text.lower()


        # JIRA ticket handling
        handleTickets(text, user, channel)

        # !cmd handling
        handleCommands(text, user, channel)

        
        

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Start flask server on port 3000
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=3000)
