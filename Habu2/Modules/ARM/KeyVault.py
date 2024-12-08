import requests
import json
from rich.progress import track

import Modules.ARM.Resources


def GetKeyVaultURI(vaults, accesstoken, apiversion, useragent):
    try:
        headers={"Authorization": f"Bearer {accesstoken}"}

        if useragent:
            headers.update({"User-Agent": useragent})

        for vault in vaults:
        
            response = requests.get(f"https://management.azure.com{vault['id']}?api-version={apiversion}", headers=headers)
            
            if response.status_code == 200:
                vaults.remove(vault)
                vaults.append(json.loads(response.content.decode("utf-8")))
                
        response = vaults
    except Exception as e:
        response = e
    finally: 
        return response

def GetKeyVaultSecret(vaults, keyvaultaccesstoken, useragent):
    try:
        headers={"Authorization": f"Bearer {keyvaultaccesstoken}"}
        
        if useragent:
            headers.update({"User-Agent": useragent})

        for vault in track(vaults, "Eumerating Key Vaults..."):
            response = requests.get(f"{vault['properties']['vaultUri']}/secrets/?api-version=7.4", headers=headers)
            
            if response.status_code == 200:
                secrets = json.loads(response.content.decode("utf-8"))["value"]
                secretsList = []

                for secret in secrets:
                    secretValue = requests.get(f"{secret['id']}?api-version=7.4", headers=headers)
                    
                    if secretValue.status_code == 200:
                        secretsList.append({secret["id"]: json.loads(secretValue.content.decode("utf-8"))})
                
                vault.update({"secrets": secretsList})
            else:
                vault.update({"secrets": None})

            response = vaults
    except Exception as e:
        response = e
    finally: 
        return response
    
def GetKeyVaultKey(args, vaults):
    pass

def GetKeyVaultCertificate(args, vaults):
    pass