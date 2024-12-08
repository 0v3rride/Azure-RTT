# https://learn.microsoft.com/en-us/rest/api/storageservices/list-blobs?tabs=microsoft-entra-id
# https://learn.microsoft.com/en-us/rest/api/storageservices/

import requests
import io
import re
import pathlib
import xmltodict
from rich import print
from urllib import parse
from rich.progress import track
import multiprocessing

storageType = {
    "blob": "blob.core.windows.net",
    "file": "file.core.windows.net",
    "table" "table.core.windows.net"
    "queue": "queue.core.windows.net",
    "data lake": "dfs.core.windows.net"
}


# def BruteContainers(accesstoken, storageaccounts, sastoken, wordlist, parameters, listblobs, useragent, apiversion = "2024-11-04"):
#     containerList = multiprocessing.Manager().list()
#     processes = []
#     storageaccounts = storageaccounts.read().split("\n")
#     wordlist = wordlist.read().split("\n")

#     for storageaccount in storageaccounts:
#         p = multiprocessing.Process(target=RequestContainers, args=(accesstoken, storageaccount, sastoken, wordlist, parameters, listblobs, useragent, containerList, apiversion))
#         p.start()
#         processes.append(p)

#     for process in processes:
#         process.join()

#     return containerList


# def RequestContainers(accesstoken, storageaccount, sastoken, wordlist, parameters, listblobs, useragent, containerList, apiversion = "2024-11-04"):
#     try:
#         headers = {"x-ms-version": apiversion}
#         baseUrl = f"https://{storageaccount}.{storageType['blob']}"
        
#         for container in track(wordlist, description=f"Finding container names..."):
#             response = None
#             url = None

#             if sastoken:
#                 url = f"{baseUrl}/{container}/?{sastoken}&restype=container&comp=list"
#             else:
#                 url = f"{baseUrl}/{container}/?restype=container&comp=list"

#             if parameters:
#                 url = f"{url}&{parameters}"

#             if accesstoken:
#                 headers.update({"Authorization": f"Bearer {accesstoken}"})

#             if useragent:
#                 headers.update({"User-Agent": useragent})
            
#             response = requests.get(f"{url}", headers=headers)
            
#             if response.status_code == 200:
#                 print(f"[bold green][+][/bold green] Found container: {url}")
                
#                 if listblobs:
#                     containerList.append({"url": url, "blobs": xmltodict.parse(response.content.decode("utf-8"))["EnumerationResults"]["Blobs"]})
#                 else:
#                     containerList.append({"url": url})
#     except Exception as e:
#         response = e
#     finally:
#         return response

def BruteContainers(accesstoken, storageaccount, sastoken, wordlist, parameters, listblobs, useragent, apiversion = "2024-11-04"):
    try:
        headers = {"x-ms-version": apiversion}
        baseUrl = f"https://{storageaccount}.{storageType['blob']}"
        wordlist = wordlist.read().split("\n")

        containerList = []
        
        for container in track(wordlist, description="Finding container names..."):
            response = None
            url = None

            if sastoken:
                url = f"{baseUrl}/{container}/?{sastoken}&restype=container&comp=list"
            else:
                url = f"{baseUrl}/{container}/?restype=container&comp=list"

            if parameters:
                url = f"{url}&{parameters}"

            if accesstoken:
                headers.update({"Authorization": f"Bearer {accesstoken}"})

            if useragent:
                headers.update({"User-Agent": useragent})
            
            response = requests.get(f"{url}", headers=headers)
            
            if response.status_code == 200:
                print(f"[bold green][+][/bold green] Found container: {url}")
                
                if listblobs:
                    containerList.append({"url": url, "blobs": xmltodict.parse(response.content.decode("utf-8"))["EnumerationResults"]["Blobs"]})
                else:
                    containerList.append({"url": url})
            
            if len(containerList) > 0:
                response = containerList
            else:
                response = "No valid containers found!"
    except Exception as e:
        response = e
    finally:
        return response


def Extract(lootPath, safeAccountName, safeContainerName, blobName, rawBlob):
    writeSuccess = False

    try:
        pathlib.Path(f"{lootPath}{safeAccountName}-{safeContainerName}").mkdir(parents=True, exist_ok=True)
        
        with io.open(f"{lootPath}{safeAccountName}-{safeContainerName}/{blobName}", "wb") as blob:
            blob.write(rawBlob)

        writeSuccess = True
        
    except Exception as e:
        writeSuccess = False
    finally:
        return writeSuccess


def GetBlob(accesstoken, storageaccount, container, blobname, sastoken, lootpath, parameters, useragent, apiversion = "2024-11-04"):
    try:
        headers = {"x-ms-version": apiversion}
        baseUrl = None

        if blobname:
            baseUrl = f"https://{storageaccount}.{storageType['blob']}/{container}/{parse.quote(blobname)}"
        else:
            baseUrl = f"https://{storageaccount}.{storageType['blob']}/{container}?restype=container&comp=list"
        
        url = baseUrl
        listBlobs = re.search("restype=container&comp=list", baseUrl)
        response = None
        
        if sastoken and listBlobs:
            url = f"{baseUrl}&{sastoken}"
        elif sastoken:
            url = f"{baseUrl}?{sastoken}"

        if parameters and (sastoken or listBlobs):
            url = f"{url}&{parameters}"
        elif parameters:
            url = f"{url}?{parameters}"

        if accesstoken:
            headers.update({"Authorization": f"Bearer {accesstoken}"})

        if useragent:
            headers.update({"User-Agent": useragent})
        
        response = requests.get(f"{url}", headers=headers)
        
        if response.status_code == 200:
            if listBlobs:
                response = xmltodict.parse(response.content.decode("utf-8"))
            else:
                rawBlob = response.content

                safeSAN = "".join(c for c in storageaccount if c.isalpha() or c.isdigit() or c==' ').rstrip()
                safeCN = "".join(c for c in container if c.isalpha() or c.isdigit() or c==' ').rstrip()

                result = Extract(lootpath, safeSAN, safeCN, blobname, rawBlob)
                
                if result:
                    response = {
                        "url": url,
                        "lootPath": f"{lootpath}/{safeSAN}-{safeCN}/{blobname}"
                    }
        
    except Exception as e:
        response = e
    finally:
        return response
    

def GetContainer(accesstoken, storageaccount, sastoken, parameters, useragent, apiversion = "2024-11-04"):
    try:
        headers = {"x-ms-version": apiversion}
        baseUrl = f"https://{storageaccount}.{storageType['blob']}/?comp=list"
        
        url = baseUrl
        response = None
        
        if sastoken:
            url = f"{url}&{sastoken}"

        if parameters:
            url = f"{url}&{parameters}"

        if accesstoken:
            headers.update({"Authorization": f"Bearer {accesstoken}"})

        if useragent:
            headers.update({"User-Agent": useragent})
        
        response = requests.get(f"{url}", headers=headers)
        
        if response.status_code == 200:
            response = xmltodict.parse(response.content.decode("utf-8"))
        
    except Exception as e:
        response = e
    finally:
        return response
    

# def ListBlob(accesstoken, storageaccount, container, sastoken, parameters, useragent, apiversion = "2024-11-04"):
#     try:
#         headers = {"x-ms-version": apiversion}
#         baseUrl = f"https://{storageaccount}.{storageType['blob']}/{container}?restype=container&comp=list"
        
#         url = baseUrl
#         response = None
        
#         if sastoken:
#             url = f"{baseUrl}&{sastoken}"

#         if parameters:
#             url = f"{url}&{parameters}"

#         if accesstoken:
#             headers.update({"Authorization": f"Bearer {accesstoken}"})

#         if useragent:
#             headers.update({"User-Agent": useragent})
        
#         response = requests.get(f"{url}", headers=headers)
        
#         if response.status_code == 200:
#             response = xmltodict.parse(response.content.decode("utf-8"))
        
#     except Exception as e:
#         response = e
#     finally:
#         return response