import requests
import json
from rich.progress import track

# def GetDirectoryRole(accesstoken, unitid, params, useragent):
#     url = f"https://graph.microsoft.com/v1.0/users/{unitid}"
#     headers = {"Authorization": f"Bearer {accesstoken}"}

#     if useragent:
#         headers.update({"User-Agent": useragent})

#     if params:
#         url = f"https://graph.microsoft.com/v1.0/users/{unitid}?{params}"

#     try:
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             user = json.loads(response.content.decode("utf-8"))
#         else:
#             print(tabulate.tabulate([["❌", response.text]]))
#     except Exception as e:
#         print(tabulate.tabulate([["❌", e]]))
#     finally:
#         return user


def GetAllDirectoryRoles(accesstoken, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/directoryRoles"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            roles = json.loads(response.content.decode("utf-8"))["value"]

            if len(roles) > 0:
                for role in track(roles, "Enumerating Entra Roles..."):

                    members = (GetDirectoryRoleMembers(accesstoken, role["id"], useragent) if not None else None)
                    role.update({"members": members})

                response = roles
            else:
                response = "No directory roles were found!"
    except Exception as e:
        response = e
    finally:
        return response


def GetDirectoryRoleMembers(accesstoken, id, useragent):
    url = f"https://graph.microsoft.com/v1.0/directoryRoles/{id}/members"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            membersList = []
            members = json.loads(response.content.decode("utf-8"))["value"]

            if len(members) > 0:
                for member in members:
                    match member["@odata.type"]:
                        case "#microsoft.graph.group":
                            membersList.append({"type": member["@odata.type"], "id": member["id"], "displaName": member["displayName"]})
                        case "#microsoft.graph.user":
                            membersList.append({"type": member["@odata.type"], "id": member["id"], "userPrincipalName": member["userPrincipalName"]})
                        case "#microsoft.graph.role":
                            membersList.append({"type": member["@odata.type"], "id": member["id"], "displaName": member["displayName"]})
                
                response = membersList
            else:
                response = None
    except Exception as e:
        response = e
    finally:
        return response