import requests
import json
from rich.progress import track


# def GetAdministrativeUnit(accesstoken, id, params, useragent):
#     url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{id}"
#     headers = {"Authorization": f"Bearer {accesstoken}"}
#     response = None

#     if useragent:
#         headers.update({"User-Agent": useragent})

#     if params:
#         url = f"{url}?{params}"

#     try:
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             unit = json.loads(response.content.decode("utf-8"))
#             print(unit)

#             if isinstance(unit, dict) > 0:
#                 # Get scoped members of the unit
#                 scopedMembersResponse = GetScopedMembers(accesstoken, unit["id"], useragent)
                
#                 if scopedMembersResponse.status_code == 200:
#                     scopedMembersList = []
#                     scopedMembers = json.loads(scopedMembersResponse.content.decode("utf-8"))["value"]

#                     if len(scopedMembers) > 0:
#                         unit.update({"roleId": scopedMembers[0]["roleId"]})
                        
#                         for scopedMember in scopedMembers:
#                             scopedMembersList.append(scopedMember["roleMemberInfo"]["displayName"])

#                             # match member["@odata.type"]:
#                             #     case "#microsoft.graph.group":
#                             #         membersList.append({"type": member["@odata.type"], "id": member["id"], "displaName": member["displayName"]})
#                             #     case "#microsoft.graph.user":
#                             #         membersList.append({"type": member["@odata.type"], "id": member["id"], "userPrincipalName": member["userPrincipalName"]})
#                             #     case "#microsoft.graph.role":
#                             #         membersList.append({"type": member["@odata.type"], "id": member["id"], "displaName": member["displayName"]})
                        
#                         unit.update({"scopedMembers": scopedMembersList})
#                     else:
#                         unit.update({"scopedMembers": None})
                    
#                     # Get members of the unit
#                     membersResponse = GetAdministrativeUnitMembers(accesstoken, unit["id"], useragent)
                    
#                     if membersResponse.status_code == 200:
#                         membersList = []
#                         members = json.loads(membersResponse.content.decode("utf-8"))["value"]

#                         if len(members) > 0:
#                             for member in members:
#                                  match member["@odata.type"]:
#                                     case "#microsoft.graph.group":
#                                         membersList.append({"type": member["@odata.type"], "id": member["id"], "displaName": member["displayName"]})
#                                     case "#microsoft.graph.user":
#                                         membersList.append({"type": member["@odata.type"], "id": member["id"], "userPrincipalName": member["userPrincipalName"]})
#                                     case "#microsoft.graph.role":
#                                         membersList.append({"type": member["@odata.type"], "id": member["id"], "displaName": member["displayName"]})
                            
#                             unit.update({"members": membersList})
#                         else:
#                             unit.update({"members": None})

#                     response = {
#                         "status_code": 200,
#                         "content": unit
#                     }
#             else:
#                 response = {
#                     "status_code": 404,
#                     "content": "No administrative units were found!"
#                 }
#     except Exception as e:
#         response = {
#             "status_code": 405,
#             "content": e
#         }
#     finally:
#         return response


def GetAllAdministrativeUnits(accesstoken, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            units = json.loads(response.content.decode("utf-8"))["value"]

            if len(units) > 0:
                for unit in track(units, "Enumerating Administrative Units..."):
                    scopedMembers = (GetScopedMembers(accesstoken, unit["id"], useragent) if not None else None)
                    unit.update({"roleId": scopedMembers["roleId"]})
                    unit.update({"scopedMembers": scopedMembers["scopedMembers"]})

                    members = (GetAdministrativeUnitMembers(accesstoken, unit["id"], useragent) if not None else None)
                    unit.update({"members": members})
                
                response = units
            else:
                response = "No administrative units were found!"
    except Exception as e:
        response = e
    finally:
        return response


def GetScopedMembers(accesstoken, id, useragent):
    url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{id}/scopedRoleMembers"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    response = None
    roleId = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            scopedMembersList = []
            scopedMembers = json.loads(response.content.decode("utf-8"))["value"]
            if len(scopedMembers) > 0:
                roleId = scopedMembers[0]["roleId"]
                
                for scopedMember in scopedMembers:
                    if "userPrincipalName" in scopedMember["roleMemberInfo"]:
                        scopedMembersList.append({"id": scopedMember["roleMemberInfo"]["id"], "userPrincipalName": scopedMember["roleMemberInfo"]["userPrincipalName"]})
                    else:
                        scopedMembersList.append({"id": scopedMember["roleMemberInfo"]["id"], "displayName": scopedMember["roleMemberInfo"]["displayName"]})

                response = {"roleId": roleId, "scopedMembers": scopedMembersList}
            else:
                response = None 
    except Exception as e:
        response = e
    finally:
        return response


def GetAdministrativeUnitMembers(accesstoken, id, useragent):
    url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{id}/members"
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