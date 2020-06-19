# Talaria

### Description
Talaria is a bot that scans messages of any channel it is added to, and responds accordingly:

- If the JIRA ticket prefixes DEV- , PP- , SC- , or ASIAQNT- are conatined within the message, Talaria will respond with a link to the corresponding JIRA ticket.
- It does not matter what case the prefixes are in (dev- , DEV- , and dEv- will all work the same).
- Lines beginning with "!" are commands, currently supported commands are !help, !thank, and !request.


### Use
Talaria only needs to run on one server to function. Once running, it can be accessed by adding it to any channel on a Slack server.
