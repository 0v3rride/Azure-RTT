import requests
import json
import xmltodict
from rich.progress import track

def GetSite(sites, accesstoken, useragent, apiversion="2023-12-01"):
    try:
        headers={"Authorization": f"Bearer {accesstoken}"}
        
        if useragent:
            headers.update({"User-Agent": useragent})

        for site in track(sites, "Eumerating Web Apps..."):
            response = requests.get(f"https://management.azure.com{site['id']}?api-version={apiversion}", headers=headers)

            if response.status_code == 200:
                sites.remove(site)
                site = json.loads(response.content.decode("utf-8"))

                data = {
                    "format": "ftp",
                    "includeDisasterRecoveryEndpoints": True
                }

                publishprofile = requests.post(f"https://management.azure.com{site['id']}/publishxml?api-version={apiversion}", headers=headers, data=data)

                if publishprofile.status_code == 200:
                    site.update({"publishProfile": xmltodict.parse(publishprofile.content.decode("utf-8"))})
                else:
                    site.update({"publishProfile": None})

                sites.append(site)

            response = sites
    except Exception as e:
        response = e
    finally: 
        return response