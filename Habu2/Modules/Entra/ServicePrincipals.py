import requests
import json


def GetServicePrincipal(accesstoken, id, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{id}"
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if parameters:
        url = f"{id}?{parameters}"

    try:
        response = requests.get(url, headers=headers)
        
    except Exception as e:
        response = e
    finally:
        return response


def GetAllServicePrincipals(accesstoken, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/servicePrincipals"
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