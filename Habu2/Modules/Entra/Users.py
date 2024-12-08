#don't forget about getting custom security attributes for users
#https://learn.microsoft.com/en-us/entra/identity/users/users-custom-security-attributes?tabs=ms-graph


import requests
import json



# def GetCurrentUser(accesstoken, userid, parameters, useragent):
#     url = f"https://graph.microsoft.com/v1.0/me"
#     headers={"Authorization": f"Bearer {accesstoken}"}

#     if useragent:
#         headers.update({"User-Agent": useragent})

#     if parameters:
#         url = f"https://graph.microsoft.com/v1.0/users/me?{parameters}"

#     try:
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             user = json.loads(response.content.decode("utf-8"))
#         else:
#             user = json.loads(response.content.decode("utf-8"))
#     except Exception as e:
#         user = e
#     finally:
#         return user


def GetUser(accesstoken, userid, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/users/{userid}"
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if parameters:
        url = f"{url}?{parameters}"

    try:
        response = requests.get(url, headers=headers)
        
    except Exception as e:
        response = e
    finally:
        return response


def GetAllUsers(accesstoken, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/users"
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if parameters:
        url = f"{url}?{parameters}"

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        response = e
    finally:
        return response


# https://learn.microsoft.com/en-us/graph/api/user-update?view=graph-rest-1.0&tabs=http
def UpdateUser(accesstoken, id, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/users/{id}"
    headers={"Authorization": f"Bearer {accesstoken}", "Content-Type": "application/json"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.post(url, headers=headers, json=json.loads(parameters))
    except Exception as e:
        response = e
    finally:
        return response