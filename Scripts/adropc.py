import requests
import json
import getpass 

client_ids = {
    "Office" : "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "PowerShell": "1950a258-227b-4e31-a9cf-717495945fc2",
    "Graph": "00000003-0000-0000-c000-000000000000",
    "WCSS": "89bee1f7-5e6e-4d8a-9f3d-ecd601259da7"
}

resources = {
    "Graph": "https://graph.microsoft.com",
}

tenant_ids = {
    "Test": "<tenant-id-here>"
}


def ROPC():
    user = input("Enter username: ")
    passwd = getpass.getpass(prompt="Enter password: ")

    body = {
        "client_id" : client_ids["Office"],
        "resource" : resources["Graph"],
        "username" : user,
        "password" : passwd,
        "grant_type" : "password"
    }

    try:
        response = requests.post("https://login.microsoftonline.com/{}/oauth2/token".format(tenant_ids["Test"]), data=body)
        
        tokens = json.loads(response.content.decode("utf-8"))

        print(tokens)
        
        data = f"Scope:\n{'-'*50}\n{tokens['scope']}\n\nResource:\n{'-'*50}\n{tokens['resource']}\n\nAccess Token:\n{'-'*50}\n{tokens['access_token']}\n\nRefresh Token:\n{'-'*50}\n{tokens['refresh_token']}"
    except Exception as e:
        data = f"An error occurred: {e}\nUsername or password may be invalid\nNote: ROPC is not supported in a hybrid identity federation (ADFS) setup!"
    finally:
        return data
