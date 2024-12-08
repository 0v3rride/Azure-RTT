import requests
import base64
import json
import io
import pathlib


def KuduCommand(kuduuri, user, password, command, dir, useragent):
    headers={
        "Authorization": f"Basic {base64.b64encode(f'{user}:{password}'.encode()).decode()}", 
        "If-Match": "*",
        "Content-Type": "application/json"
    }

    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    body = {
        "command": command,
        "dir": dir
    }

    try:
        response = requests.post(f"{kuduuri}/api/command", data=json.dumps(body), headers=headers)

    except Exception as e:
        response = e
    finally:
        return response


def KuduDownload(kuduuri, user, password, file, lootpath, useragent):
    headers={
        "Authorization": f"Basic {base64.b64encode(f'{user}:{password}'.encode()).decode()}"
    }

    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.get(f"{kuduuri}/api/vfs/{file}", headers=headers)

        if response.status_code == 200:
        
            appname = kuduuri.split("/")[2].split(".")[0]
            safeappname = "".join(c for c in appname if c.isalpha() or c.isdigit() or c==' ').rstrip()

            try:
                pathlib.Path(f"{lootpath}{safeappname}").mkdir(parents=True, exist_ok=True)
                
                with io.open(f"{lootpath}{safeappname}/{file.split('/')[-1]}", "wb") as rawBytes:
                    rawBytes.write(response.content)

                response = {
                    "lootpath": f"{lootpath}{safeappname}/{file.split('/')[-1]}"
                }
                
            except Exception as e:
                response = e
            finally:
                return response


    except Exception as e:
        response = e
    finally:
        return response


def KuduUpload(kuduuri, user, password, file, dir, useragent):
    headers={
        "Authorization": f"Basic {base64.b64encode(f'{user}:{password}'.encode()).decode()}", 
        "If-Match": "*",
    }

    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.put(f"{kuduuri}/api/vfs/{dir}{pathlib.Path(file.name).name}", files={"file": file.read()}, headers=headers)

        if response.status_code == 201:
            response = {
                "scmurl": kuduuri,
                "filepath": f"{dir}{pathlib.Path(file.name).name}"
            }

    except Exception as e:
        response = e
    finally:
        return response
    
    

    