# https://www.netspi.com/blog/technical-blog/cloud-penetration-testing/enumerating-azure-services/
# https://notsosecure.com/cloud-services-enumeration-aws-azure-and-gcp
import requests
import io

import Modules.Settings.Locations

services = {
    "website": "{}.azurewebsites.net",
    "management": "{}.scm.azurewebsites.net",
    "services": "{}.p.azurewebsites.net",
    "blob": "{}.blob.core.windows.net",
    "file": "{}.files.core.windows.net",
    "table": "{}.table.core.windows.net",
    "queue": "{}.queue.core.windows.net",
    "cloudapp": "{}.cloudapp.net",
    "microsoft hosted domain": "{}.onmicrosoft.com",
    "mail": "{}.mail.protection.outlook.com",
    "sharepoint": ["{}.sharepoint.com", "{}-my.sharepoint.com"],
    "cdn": "{}.azureedge.net",
    "search appliance": "{}.search.windows.net",
    "api service": "{}.azure-api.net",
    "key vault": "{}.vault.azure.net",
    "redis": "{}.redis.cache.windows.net",
    "cosmos db": "{}.documents.azure.com",
    "sql": "{}.database.windows.net",
    "devops": "dev.azure.com/{}",
    "app config": "{}.azconfig.io",
    "signalr": "{}.service.signalr.net",
    "azureml": "{}.azureml.net",
    "containerapps": "{}.{}.azurecontainerapps.io"
}


def EnumerateServices(args):
    response = None
    words = None

    try:
        if args.wordlist:
            with io.open(args.wordlist, "r") as wordlist:
                words = wordlist.readlines()
        elif args.baseword:
            words = [args.baseword]

        
        headers = {}

        if args.useragent:
            headers.update({"User-Agent": args.useragent})

    
        for word in words:
            for name, uri in services.items():
                if name == "containerapps":
                    for location in Modules.Settings.Locations.location:
                        suri = uri.format(word, location)
                else:
                    suri = uri.format(word)

                    response = requests.get(f"https://{suri}", headers=headers)
                    
                    if response.status_code in [200, 202, 204, 301, 302, 401, 405]:
                        print(suri)
                    else:
                        print(response.status_code)
            

    except Exception as e:
        response = e
    finally:
        return response