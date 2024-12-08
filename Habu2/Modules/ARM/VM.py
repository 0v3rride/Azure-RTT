import requests
import json
from rich.progress import track
import base64


def GetVM(vms, accesstoken, apiversion, useragent):
    try:

        vmList = []
        for vm in vms:
            headers={"Authorization": f"Bearer {accesstoken}"}

            if useragent:
                headers.update({"User-Agent": useragent})
            
            response = requests.get(f"https://management.azure.com{vm['id']}?api-version={apiversion}", headers=headers)
            
            if response.status_code == 200:
                vm = requests.get(f"https://management.azure.com{vm['id']}?$expand=userData&api-version={apiversion}", headers=headers)
                vm = json.loads(vm.content.decode("utf-8"))

                if 'userData' in vm['properties']:
                    vm['properties']['userData'] = base64.b64decode(vm['properties']['userData']).decode("utf-8")
                else:
                    vm['properties']['userData'] = None
                
            vmList.append(vm)
                
        response = vmList
    except Exception as e:
        response = e
    finally: 
        return response
