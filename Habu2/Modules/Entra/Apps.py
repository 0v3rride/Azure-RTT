import requests
import json


def GetApplication(accesstoken, id, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/applications/{id}"
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


def GetAllApplications(accesstoken, parameters, useragent):
    url = f"https://graph.microsoft.com/v1.0/applications"
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