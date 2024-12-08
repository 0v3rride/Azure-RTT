import requests
import json
from rich.progress import track

def GetResources(accesstoken, subscriptions, parameters, useragent, apiversion = "2021-04-01"):
    resourceList = []
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        for subscription in track(subscriptions, "Enumerating Resources..."):
            url = f"https://management.azure.com/subscriptions/{subscription['subscriptionId']}/resources?&api-version={apiversion}"
            
            if parameters:
                url = f"{url}&{parameters}"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                for vault in json.loads(response.content.decode("utf-8"))["value"]:
                    resourceList.append(vault)
            
            if len(resourceList) > 0:
                response = resourceList
            else:
                response = "No resources found!"
    except Exception as e:
        response = e
    finally:
        return response

