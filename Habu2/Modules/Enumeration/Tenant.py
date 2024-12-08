#https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-unauthenticated-enum-and-initial-entry
#https://stmxcsr.com/micro/o365-aad.html

import requests
import xmltodict

def GetTenantRegisteredDomains(tenant, useragent):
    url = f"https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc"
    
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation",
        "User-Agent": useragent
    }

    body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:exm="http://schemas.microsoft.com/exchange/services/2006/messages" xmlns:ext="http://schemas.microsoft.com/exchange/services/2006/types" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <soap:Header>
                <a:Action soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action>
                <a:To soap:mustUnderstand="1">https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc</a:To>
                <a:ReplyTo>
                        <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                </a:ReplyTo>
        </soap:Header>
        <soap:Body>
                <GetFederationInformationRequestMessage xmlns="http://schemas.microsoft.com/exchange/2010/Autodiscover">
                        <Request>
                                <Domain>{tenant}</Domain>
                        </Request>
                </GetFederationInformationRequestMessage>
        </soap:Body>
</soap:Envelope>"""
    
    
    try:
        response = requests.post(url, headers=headers, data=body)

        if response.status_code == 200:
            response = xmltodict.parse(response.content.decode("utf-8"))
        else:
            response = response.content.decode("utf-8")
    except Exception as e:
        response = e
    finally:
        return response