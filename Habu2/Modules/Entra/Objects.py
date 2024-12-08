import requests
import json


def GetUserOwnedObject(accesstoken, type, id, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/{type}/{id}/ownedObjects"
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


# def GetServicePrincpalOwnedObject(args):
#     url = f"https://graph.microsoft.com/v1.0/me"
#     headers={"Authorization": f"Bearer {args.token}"}

#     if args.useragent:
#         headers.update({"User-Agent": args.useragent})

#     if args.parameters:
#         url = f"https://graph.microsoft.com/v1.0/users/me?{args.parameters}"

#     try:
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             user = json.loads(response.content.decode("utf-8"))

#             if isinstance(user, dict):
#                 user.pop('@odata.context', None)

#                 userDataTable = []
#                 userDataHeader = []
#                 for key, value in user.items():
#                     userDataTable.append(value)
#                     userDataHeader.append(key)
                
#                 print(f"\n{tabulate.tabulate([userDataTable], headers=userDataHeader)}")
#             else:
#                 print(tabulate.tabulate([["❌", "User not found!"]]))
#         else:
#             print(tabulate.tabulate([["❌", response.text]]))
#     except Exception as e:
#         user = tabulate.tabulate([["❌", e]])
#     finally:
#         return user
    

# def GetObjectById(args):
#     url = f"https://graph.microsoft.com/v1.0/me"
#     headers={"Authorization": f"Bearer {args.token}"}

#     if args.useragent:
#         headers.update({"User-Agent": args.useragent})

#     if args.parameters:
#         url = f"https://graph.microsoft.com/v1.0/users/me?{args.parameters}"

#     try:
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             user = json.loads(response.content.decode("utf-8"))

#             if isinstance(user, dict):
#                 user.pop('@odata.context', None)

#                 userDataTable = []
#                 userDataHeader = []
#                 for key, value in user.items():
#                     userDataTable.append(value)
#                     userDataHeader.append(key)
                
#                 print(f"\n{tabulate.tabulate([userDataTable], headers=userDataHeader)}")
#             else:
#                 print(tabulate.tabulate([["❌", "User not found!"]]))
#         else:
#             print(tabulate.tabulate([["❌", response.text]]))
#     except Exception as e:
#         user = tabulate.tabulate([["❌", e]])
#     finally:
#         return user