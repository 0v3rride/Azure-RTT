import requests
import webbrowser
import json
import time

tenantId = "common"
clientId = "1950a258-227b-4e31-a9cf-717495945fc2"
resourceURI = "https://graph.microsoft.com"

tenantId = input("Tenant ID (guid, domain, <name>.onmicrosoft.com): ")


def GetDeviceCode():
    body = {
        'client_id' : clientId,
        'resource' : resourceURI
    }

    response = requests.post(url=f"https://login.microsoftonline.com/{tenantId}/oauth2/devicecode", data=body)
    content = json.loads(response.content.decode("UTF-8"))

    print(f"A new browser window will open. Please input {content['user_code']}. Please input this code and authenticate within 30 seconds.")

    webbrowser.open(content['verification_url'], autoraise=True, new=1)

    time.sleep(30)

    return content


def GetTokens(content):
    try:
        body = {
            'client_id' : clientId,
            'grant_type' : "urn:ietf:params:oauth:grant-type:device_code",
            'code' : content['device_code']
        }

        oauthURI = f"https://login.microsoftonline.com/{tenantId}/oauth2/token"

        response = requests.post(url=oauthURI, data=body)

        tokens = json.loads(response.content.decode("UTF-8"))

        data = f"Scope:\n{'-'*50}\n{tokens['scope']}\n\nResource:\n{'-'*50}\n{tokens['resource']}\n\nBearer/Access Token:\n{'-'*50}\n{tokens['access_token']}\n\nRefresh Token:\n{'-'*50}\n{tokens['refresh_token']}\n\nID Token:\n{'-'*50}\n{tokens['id_token']}"
    except Exception as e:
        data = f"An error occurred: {e}"
    finally:
        return data


content = GetDeviceCode()
print(GetTokens(content))
