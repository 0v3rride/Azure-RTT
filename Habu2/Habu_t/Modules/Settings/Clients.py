#https://learn.microsoft.com/en-us/troubleshoot/azure/entra/entra-id/governance/verify-first-party-apps-sign-in
#https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/how-to-retrieve-an-azure-ad-bulk-token-with-powershell/ba-p/2944894

Client = {
    "office" : "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "office portal": "00000006-0000-0ff1-ce00-000000000000",
    "office web apps": "Microsoft Office Web Apps Service",
    "teams": "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
    "azure portal": "c44b4083-3bb0-49c1-b47d-974e53cbdf3c",
    "azure powershell": "1950a258-227b-4e31-a9cf-717495945fc2",
    "azure cli": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
    "graph api": "1b730954-1685-4b74-9bfd-dac224a7b894",
    "defender portal": "a3b79187-70b2-4139-83f9-6016c58cd27b",
    "defender for cloud apps": "3090ab82-f1c1-4cdf-af2c-5d7a6f3e2cc7"
    # "Graph": "00000003-0000-0000-c000-000000000000",
    # "WCSS": "89bee1f7-5e6e-4d8a-9f3d-ecd601259da7",
    # "EWS": "47629505-c2b6-4a80-adb1-9b3a3d233b7b",
    # "Exchange Online": "00000002-0000-0ff1-ce00-000000000000",
    # "Windows Azure Service Management API": "797f4846-ba00-4fd7-ba43-dac1f8f63013",
    # "WindowsDefenderATP Portal": "a3b79187-70b2-4139-83f9-6016c58cd27b"
}


def GetClientId(name):
    try:
        return Client.get(name, name)
    except KeyError as ke:
        return name