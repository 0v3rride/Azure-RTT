import requests
from rich import print
from urllib import parse

# https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery?view=graph-rest-1.0&tabs=http


def RunQuery(accesstoken, query, timespan, useragent):
    try:
        headers = {"Authorization": f"Bearer {accesstoken}"}

        data = {
            "Query": f"{query}",
            "Timespan": f"{timespan}"
        }
        
        if useragent:
            headers.update({"User-Agent": useragent})
        
        response = requests.post("https://graph.microsoft.com/v1.0/security/runHuntingQuery", headers=headers, data=data)
        
        if response.status_code == 200:
            print(response.text)
        
    except Exception as e:
        response = e
    finally:
        return response