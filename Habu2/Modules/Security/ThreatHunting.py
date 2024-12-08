import requests
from rich import print
import getpass
import json

import Authentication.Selenium
# https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery?view=graph-rest-1.0&tabs=http
# Burp suite - security.microsoft.com/apiproxy/mtp/huntingService/queryExecutor?useFanOut=false; sccauth; x-xsrf-token
# https://www.reddit.com/r/DefenderATP/comments/w9cj8y/pushing_detection_rules_programmatically/
# https://github.com/fooop/DefenderDetectionSync
# https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x04-timeline-3f01282839e4
# https://falconforce.nl/microsoft-defender-for-endpoint-internals-0x05-telemetry-for-sensitive-actions/
# https://github.com/fahri314/365-Defender-Rule-Activator
# https://github.com/search?q=%2Fapiproxy%5C%2Fmtp%5C%2Fhunting%2F&type=code
# https://github.com/search?q=%2Fsecurity%5C.microsoft%5C.com%5C%2Fapiproxy%5C%2Fmtp%2F&type=code
# https://security.microsoft.com/v2/advanced-hunting?tid=tenantidoralias

def SeleniumRunQuery(username, password, sccauthtoken, xsrftoken, query, start, end, maxrecords, useragent):

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

        data = {
            "QueryText": f"{query}",
            "StartTime": start,
            "EndTime": end,
            "MaxRecordCount": maxrecords 
        }
        
        if useragent:
            headers.update({"User-Agent": useragent})
        
        response = requests.post("https://security.microsoft.com/apiproxy/mtp/huntingService/queryExecutor?useFanOut=false", headers=headers, json=data)

        print(response.text)
        if response.status_code == 440:
            response = "[bold red][-][/bold red] Tokens are expired. Re-authenticate for new tokens."
        else:
            response = json.loads(response.content.decode("utf-8"))["Results"]
        
    except Exception as e:
        response = e
    finally:
        return response
    

def MTPRunQuery(accesstoken, query, start, end, maxrecords, useragent):
    try:
        headers = {
            "Authorization": f"Bearer {accesstoken}",
        }

        data = {
            "QueryText": f"{query}",
            "StartTime": start,
            "EndTime": end,
            "MaxRecordCount": maxrecords 
        }
        
        if useragent:
            headers.update({"User-Agent": useragent})
        
        response = requests.post("https://m365d-hunting-api-prd-weu.securitycenter.windows.com/api/ine/huntingservice/queryExecutor?useFanOut=false", headers=headers, json=data)

        if response.status_code == 200:
            response = json.loads(response.content.decode("utf-8"))["Results"]
        else:
            response = "[bold red][-][/bold red] Unable to run query! Check token and try again."
        
    except Exception as e:
        response = e
    finally:
        return response