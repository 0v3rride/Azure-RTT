import requests
import json
from rich.progress import track

def GetAllGroups(accesstoken, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/groups"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            groups = json.loads(response.content.decode("utf-8"))["value"]

            if len(groups) > 0:
                for group in track(groups, "Enumerating groups..."):

                    members = (GetMembers(accesstoken, group["id"], useragent) if not None else None)
                    group.update({"members": members})

                response = groups
            else:
                response = "No groups were found!"
    except Exception as e:
        response = e
    finally:
        return response


def GetMembers(accesstoken, id, useragent):
    url = f"https://graph.microsoft.com/v1.0/groups/{id}/members"
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