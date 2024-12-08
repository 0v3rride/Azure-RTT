import requests
import json
import xmltodict
from rich.progress import track

#https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/list-functions?view=rest-appservice-2023-12-01
def GetFunction(functions, accesstoken, useragent, apiversion="2023-12-01"):
    try:
        response = None
        headers={"Authorization": f"Bearer {accesstoken}"}
        
        if useragent:
            headers.update({"User-Agent": useragent})

        for function in track(functions, "Eumerating Function Apps..."):
            response = requests.get(f"https://management.azure.com{function['id']}?api-version={apiversion}", headers=headers)

            if response.status_code == 200:
                functions.remove(function)
                function = json.loads(response.content.decode("utf-8"))

                data = {
                    "format": "ftp",
                    "includeDisasterRecoveryEndpoints": True
                }

                publishprofile = requests.post(f"https://management.azure.com{function['id']}/publishxml?api-version={apiversion}", headers=headers, data=data)

                if publishprofile.status_code == 200:
                    function.update({"publishProfile": xmltodict.parse(publishprofile.content.decode("utf-8"))})
                else:
                    function.update({"publishProfile": None})

                functionappfunctions = requests.get(f"https://management.azure.com{function['id']}/functions?api-version={apiversion}", headers=headers)

                if functionappfunctions.status_code == 200:
                    function.update({"appFunctions": json.loads(functionappfunctions.content.decode("utf-8"))})
                else:
                    function.update({"appFunctions": None})

                functions.append(function)

            response = functions
    except Exception as e:
        response = e
    finally: 
        return response