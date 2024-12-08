# https://learn.microsoft.com/bs-latn-ba/azure/role-based-access-control/role-assignments-list-rest
# https://learn.microsoft.com/en-us/azure/role-based-access-control/role-definitions-list
import requests
import json
from rich.progress import track


def GetRoleAssignments(accesstoken, subscriptions, parameters, useragent, apiversion = "2022-04-01"):
    roleList = []
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        for subscription in subscriptions:
            url = f"https://management.azure.com{subscription['id']}/providers/Microsoft.Authorization/roleAssignments?api-version={apiversion}"
            
            if parameters:
                url = f"{url}&{parameters}"

            response = requests.get(url, headers=headers)
            

            if response.status_code == 200:
                roleAssignments = json.loads(response.content.decode("utf-8"))["value"]
                
                for roleAssignment in track(roleAssignments, "Enumerating RBAC Roles..."):
                    url = f"https://management.azure.com{subscription['id']}/providers/Microsoft.Authorization/roleDefinitions/{str(roleAssignment['properties']['roleDefinitionId']).split('/')[-1]}?api-version={apiversion}"
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        roleAssignment.update({"roleDefinitions": json.loads(response.content.decode("utf-8"))})
                    else:
                        roleAssignment.update({"roleDefinitions": None})
                        
                    roleList.append(roleAssignment)

        if len(roleList) > 0:
            response = roleList
        else:
            response = "No role assignments found!"
            
    except Exception as e:
        response = e
    finally:
        return response