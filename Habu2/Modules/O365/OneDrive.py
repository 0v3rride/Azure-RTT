import requests
import json
import pathlib


def GetDriveItems(accesstoken, drive, useragent):
    url = f"https://graph.microsoft.com/v1.0/drives/{drive['id']}/list/items"
    headers={"Authorization": f"Bearer {accesstoken}"}
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.get(f"{url}", headers=headers)
    except Exception as e:
        response = e
    finally:
        return response
    

def GetSharedWithMe(accesstoken, useragent):
    headers={"Authorization": f"Bearer {accesstoken}"}
    url = "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe"

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        response = e
    finally:
        return response


def GetDrive(accesstoken, useragent):
    headers={"Authorization": f"Bearer {accesstoken}"}
    url = f"https://graph.microsoft.com/v1.0/me/drive"

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        response = e
    finally:
        return response


def ExtractDriveItems(accesstoken, drive, lootpath, useragent):
    headers={"Authorization": f"Bearer {accesstoken}"}
    
    if useragent:
        headers.update({"User-Agent": useragent})

    for sharedItem in drive["sharedItems"]:
        path = f"{lootpath}/{sharedItem['name']}"

        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        
        response = requests.get(f"https://graph.microsoft.com/me/drive/items/{sharedItem['id']}", headers=headers)
        print(response.text)


        
    
    # subject = "".join(c for c in subject if c.isalpha() or c.isdigit() or c==' ').rstrip()

    # pathlib.Path(f"{lootpath}{subject}").mkdir(parents=True, exist_ok=True)

    # extractPath = f"{lootpath}{subject}/{filename}"
    # file = io.open(f"{lootpath}{subject}/{filename}", mode="wb")

    # try:
    #     file.write(b64decode(rawbytes))
    # except Exception as e:
    #     print(e)
    # finally:
    #     file.close()
    #     return extractPath