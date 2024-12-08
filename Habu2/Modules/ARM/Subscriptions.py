import requests

def GetSubscriptions(accesstoken, parameters, useragent, apiversion = "2022-12-01"):
    url = f"https://management.azure.com/subscriptions?api-version={apiversion}"
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if parameters:
        url = f"{url}&{parameters}"

    try:
        response = requests.get(url, headers=headers)
        
    except Exception as e:
        response = e
    finally:
        return response