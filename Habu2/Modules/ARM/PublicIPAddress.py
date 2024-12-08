import requests
import json
from rich.progress import track

# https://learn.microsoft.com/en-us/rest/api/virtualnetwork/public-ip-addresses/list-all?view=rest-virtualnetwork-2024-03-01&tabs=HTTP

def GetPublicIPAddress(vm, accesstoken, useragent, apiversion="2024-03-01"):
    try:
        headers={"Authorization": f"Bearer {accesstoken}"}

        if useragent:
            headers.update({"User-Agent": useragent})
            
        response = requests.get(f"https://management.azure.com/{vm['id'].split('/')[0]}/providers/Microsoft.Network/publicIPAddresses?api-version={apiversion}", headers=headers)
        
        if response.status_code == 200:
            response = json.loads(response.content.decode("utf-8"))
    
    except Exception as e:
        response = e
    finally: 
        return response
