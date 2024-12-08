import requests
import json
import io
from colorama import Fore, Style
import tabulate
import html2text

#region TEAMS API INFO
# CHATGPT: The https://apac.msgapi.teams.microsoft.com (i.e. teamsSettings["regionGtms"]["chatService"]) 
# domain is part of Microsoft Teams' internal API used by the Teams clients (web, desktop, or mobile apps) to interact with the 
# Teams backend. The specific endpoints under this domain are generally not publicly documented, 
# as they are intended for use by the Teams client applications rather than for direct use by developers.

# However, some common types of endpoints you might encounter or be interested in include:

# User-related Endpoints:
# /v1/users/ME/conversations: Retrieves the list of conversations for the authenticated user.
# /v1/users/ME/conversations/{conversationId}/messages: Retrieves the messages in a specific conversation.
# /v1/users/ME/conversations/{conversationId}/members: Retrieves the members of a specific conversation.

# Conversations-related Endpoints:
# /v1/conversations: Create a new conversation.
# /v1/conversations/{conversationId}: Get details about a specific conversation.
# /v1/conversations/{conversationId}/messages: Send a message to a specific conversation.
# /v1/conversations/{conversationId}/messages/{messageId}: Retrieve, update, or delete a specific message.

# Teams-related Endpoints:
# /v1/teams/{teamId}/channels: List all channels within a specific team.
# /v1/teams/{teamId}/channels/{channelId}: Get details about a specific channel.
# /v1/teams/{teamId}/channels/{channelId}/messages: Send a message to a specific channel.

# File-related Endpoints:
# /v1/conversations/{conversationId}/files: List or upload files within a specific conversation.
# /v1/teams/{teamId}/channels/{channelId}/files: List or upload files within a specific channel.

# Notification Endpoints:
# /v1/users/ME/notifications: Retrieve or manage notifications for the authenticated user.

# These endpoints represent potential interactions with Microsoft Teams via its internal API, but the exact structure 
# and availability may differ based on the Teams client version, region, or configuration. Additionally, these endpoints 
# are generally used by the client apps, and accessing them directly might require appropriate authentication tokens and 
# could violate Microsoft's terms of service.

# For developer-focused integration, the Microsoft Graph API is the recommended way to interact with Teams data. 
# Microsoft Graph API provides documented, supported, and stable endpoints for accessing Teams-related data and functionality.
#THESE ARE NOT DEFINITIVE ENDPOINTS, BUT IT LOOKS LIKE THE "OLD" TEAMS REST API NAMING/PATH CONVENTION IS SIMILAR TO THE NEW GRAPH API CONVENTION FOR TEAMS - https://learn.microsoft.com/en-us/graph/api/resources/teams-api-overview?view=graph-rest-1.0
#endregion



# https://github.com/f-bader/TokenTacticsV2/blob/main/modules/TokenHandler.ps1
# https://github.com/dafthack/GraphRunner/blob/main/GraphRunner.ps1
    # refreshes to https://outlook.office.com//.default openid profile offline_access and does search via substrate api
# TokenTacticsv2
    # refreshes to "https://api.spaces.skype.com/.default offline_access openid" - search with another tool or api
# AADInternal
    # refreshes to "https://api.spaces.skype.com/.default offline_access openid" - search with ? -> TODO: teams tenancy - https://ash-king.co.uk/blog/Bypass-Microsoft-Teams-Tenancy-Permission
    # https://github.com/Gerenios/AADInternals/blob/master/Teams.ps1
    # 1. Use refresh token to refresh access token to api.spaces.skype.com
    # 2. Use new token to get skypetoken and teams settings wit the authsvc.teams.microsoft.com endpoint
    # 3. Use skype api/undocument endpoints to get messages, converstations, chats
    


def GetTeamsSettings(accesstoken, useragent):
    response = None
    headers={"Authorization": f"Bearer {accesstoken}"}
    
    if useragent:
        headers.update({"User-Agent": useragent})

    response = requests.post("https://authsvc.teams.microsoft.com/v1.0/authz", headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return None


def GetMessages(accesstoken, useragent):
    try:
        # https://github.com/Gerenios/AADInternals/blob/master/Teams.ps1
        # https://www.powershellgallery.com/packages/AADInternals/0.4.9/Content/Teams.ps1
        # https://skpy.t.allofti.me/background/protocol/chats.html
        # https://techcommunity.microsoft.com/t5/teams-developer/how-to-get-the-token-in-order-to-call-users-me-conversations/m-p/1279400
        # https://techcommunity.microsoft.com/t5/teams-developer/block-a-message-in-microsoft-teams/m-p/961372#
        # https://digitalworkplace365.wordpress.com/2021/01/04/using-the-ms-teams-native-api-end-points/
        # https://dnsrepo.noc.org/?domain=teams.microsoft.com.
        teamsSettings = GetTeamsSettings(accesstoken, useragent)
        chatService = None
        skypeToken = None
        messageList = []

        if teamsSettings:
            chatService = teamsSettings["regionGtms"]["chatService"]
            skypeToken = teamsSettings["tokens"]["skypeToken"]

            headers={"Authorization": f"Bearer {accesstoken}", "Authentication": f"skypetoken={skypeToken}"}

            if useragent:
                headers.update({"User-Agent": useragent})

            response = requests.get(f"{chatService}/v1/users/ME/conversations", headers=headers)
            
            if response.status_code == 200:
                conversations = json.loads(response.content.decode("utf-8"))["conversations"]

                if isinstance(conversations, list):
                    if len(conversations) > 0:

                        for conversation in conversations:
                            if conversation["id"].find("19:") > -1:
                                response = requests.get(f"{chatService}/v1/users/ME/conversations/{conversation['id']}/messages?startTime=0&view=msnp24Equivalent", headers=headers)
                                
                                if response.status_code == 200:
                                    messages = json.loads(response.content.decode("utf-8"))["messages"]
                                    if len(messages) > 0:
                                        for message in messages:
                                            messageList.append(message)
                response = messageList
            
            if len(messageList) <= 0:
                response = "[bold red][-][/bold red] No teams messages found!"
        else:
            response = "No messages found!"                     
    except Exception as e:
        response = e
    finally:
        return response