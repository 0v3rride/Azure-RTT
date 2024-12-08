#https://learn.microsoft.com/en-us/troubleshoot/azure/entra/entra-id/governance/verify-first-party-apps-sign-in
#https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/how-to-retrieve-an-azure-ad-bulk-token-with-powershell/ba-p/2944894


# https://gist.github.com/dafthack/2c0bbcac72b10c1ee205d1dd2fed3fe7
# https://github.com/0x6f677548/zerotrust-ca-powertoys/blob/f35be072974d95b8e2e67b824819e7d835e5f6b1/src/ca_pwt/applications.py#L752

Client = {
    "office" : "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "office portal": "00000006-0000-0ff1-ce00-000000000000",
    "office web apps": "Microsoft Office Web Apps Service",
    "teams": "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
    "azure portal": "c44b4083-3bb0-49c1-b47d-974e53cbdf3c",
    "azure powershell": "1950a258-227b-4e31-a9cf-717495945fc2",
    "azure cli": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
    "graph cli": "14d82eec-204b-4c2f-b7e8-296a70dab67e",
    "graph api": "1b730954-1685-4b74-9bfd-dac224a7b894",
    "defender portal": "a3b79187-70b2-4139-83f9-6016c58cd27b",
    "defender for cloud apps": "3090ab82-f1c1-4cdf-af2c-5d7a6f3e2cc7",
    # "intune": "0000000a-0000-0000-c000-000000000000",
    # "intune api": "c161e42e-d4df-4a3d-9b42-e7a3c31f59d4",
    # "intune mam": "6c7e8096-f593-4d72-807f-a5f86dcc9c77",
    # "broker": "29d9ed98-a469-4536-ade2-f981bc1d605e",
    # "drs": "dd762716-544d-4aeb-a526-687b73838a22"
    
    # use interactivebrowserbrokencredential in the msal module for this client id with the graph scope
    "intune portal": "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
    
    # Intune extensions
    "aad devices": "c40dfea8-483f-469b-aafe-642149115b3a",
    "cloud pc": "69cc3193-b6c4-4172-98e5-ed0f38ab3ff8",
    "intune portal extension": "5926fc8e-304e-4f59-8bed-58ca97cc39a4",
    "aad iam": "74658136-14ec-4630-ad9b-26e160ff0fc6",

    "security and compliance center": "80ccca67-54bd-44ab-8625-4b79c4dc7775",
    # "Graph": "00000003-0000-0000-c000-000000000000",
    # "WCSS": "89bee1f7-5e6e-4d8a-9f3d-ecd601259da7",
    #"teams web client": "5e3ce6c0-2b1f-4285-8d4b-75ee78787346",
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