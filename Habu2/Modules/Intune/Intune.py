import requests
import json
from rich.progress import track
import base64

#https://github.com/Gerenios/AADInternals/blob/9c8fd15d2a853a6d6515da15d0d81bd3e0475f6d/AzureManagementAPI_utils.ps1#L461
# def GetTokens(user, password, useragent):
#     portal_refresh_token = Tokens.MSPortalAuth.GetTokens(user, password, "intune")
#     return portal_refresh_token

def GetManagedDevice(accesstoken, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    deviceList = []
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            devices = json.loads(response.content.decode("utf-8"))["value"]

            if len(devices) > 0:
                for device in track(devices, "Gathering managed intune devices..."):
                    response = requests.get(f"https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{device['id']}", headers=headers)

                    if response.status_code == 200:
                        deviceList.append(json.loads(response.content.decode("utf-8")))
        
                response = deviceList
            else:
                response = "[bold red][-][/bold red] No managed devices found!"

    except Exception as e:
        response = e
    finally:
        return response

# https://learn.microsoft.com/en-us/graph/api/resources/cloudpc-api-overview?view=graph-rest-1.0
def GetCloudPC(accesstoken, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    cpcList = []
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            devices = json.loads(response.content.decode("utf-8"))["value"]

            if len(devices) > 0:
                for device in track(devices, "Gathering managed intune devices..."):
                    response = requests.get(f"https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs/{devices['id']}", headers=headers)

                    if response.status_code == 200:
                        cpcList.append(json.loads(response.content.decode("utf-8")))
        
                response = cpcList
            else:
                response = "[bold red][-][/bold red] No cloud PCs found!"

    except Exception as e:
        response = e
    finally:
        return response

# https://learn.microsoft.com/en-us/graph/api/resources/bitlockerrecoverykey?view=graph-rest-1.0
def GetDeviceBitLockerKey(accesstoken, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    keyList = []
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            keys = json.loads(response.content.decode("utf-8"))["value"]

            if len(keys) > 0:
                for key in track(keys, "Gathering BitLocker Keys..."):
                    response = requests.get(f"https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys/{key['id']}?$select=key", headers=headers)

                    if response.status_code == 200:
                        keyList.append(json.loads(response.content.decode("utf-8")))

                response = keyList
            else:
                response = "[bold red][-][/bold red] No keys found!"

    except Exception as e:
        response = e
    finally:
        return response

# https://learn.microsoft.com/en-us/graph/api/resources/devicelocalcredentialinfo?view=graph-rest-1.0
def GetDeviceLocalCredentials(accesstoken, clientname, clientversion, params, useragent):
    url = f"https://graph.microsoft.com/v1.0/directory/deviceLocalCredentials"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    headers.update({"ocp-client-name": clientname, "ocp-client-version": clientversion})
    credentialList = []
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}&{params}"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            credentials = json.loads(response.content.decode("utf-8"))["value"]
            
            if len(credentials) > 0:
                for credential in track(credentials, "Gather managed device local credentials..."):
                    response = requests.get(f"https://graph.microsoft.com/v1.0/directory/deviceLocalCredentials/{credential['id']}?$select=credentials", headers=headers)

                    if response.status_code == 200:
                        credentialList.append(json.loads(response.content.decode("utf-8"))["value"])
        
                response = credentialList
            else:
                response = "[bold red][-][/bold red] No local credentials found!"

    except Exception as e:
        response = e
    finally:
        return response

# https://learn.microsoft.com/en-us/graph/api/resources/intune-shared-devicemanagementscript?view=graph-rest-beta
def GetDeviceManagementScript(accesstoken, format, params, useragent):
    url = f"https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    scriptList = []
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            scripts = json.loads(response.content.decode("utf-8"))["value"]

            if len(scripts) > 0:
                for script in track(scripts, "Gathering device management scripts..."):
                    response = requests.get(f"https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts/{script['id']}", headers=headers)

                    if response.status_code == 200:
                        scriptInfo = json.loads(response.content.decode("utf-8"))

                        if format == "text":
                            scriptInfo["scriptContent"] = base64.b64decode(scriptInfo["scriptContent"]).decode("utf-8")

                        scriptList.append(scriptInfo)
        
                response = scriptList
            else:
                response = "[bold red][-][/bold red] No scripts found!"

    except Exception as e:
        response = e
    finally:
        return response

# https://learn.microsoft.com/en-us/graph/api/resources/intune-devices-deviceshellscript?view=graph-rest-beta
def GetDeviceShellScript(accesstoken, format, params, useragent):
    url = f"https://graph.microsoft.com/beta/deviceManagement/deviceShellScripts"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    scriptList = []
    response = None

    if useragent:
        headers.update({"User-Agent": useragent})

    if params:
        url = f"{url}?{params}"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            scripts = json.loads(response.content.decode("utf-8"))["value"]

            if len(scripts) > 0:
                for script in track(scripts, "Gathering shell scripts..."):
                    response = requests.get(f"https://graph.microsoft.com/beta/deviceManagement/deviceShellScripts/{script['id']}", headers=headers)

                    if response.status_code == 200:
                        scriptInfo = json.loads(response.content.decode("utf-8"))

                        if format == "text":
                            scriptInfo["scriptContent"] = base64.b64decode(scriptInfo["scriptContent"]).decode("utf-8")
                            
                        scriptList.append(scriptInfo)
        
                response = scriptList
            else:
                response = "[bold red][-][/bold red] No scripts found!"

    except Exception as e:
        response = e
    finally:
        return response

def CreateManagementScript():
    pass

def RunManagementScript():
    pass

def DeleteManagementScript():
    pass

def CreateShellScript():
    pass

def DeleteShellScript():
    pass


