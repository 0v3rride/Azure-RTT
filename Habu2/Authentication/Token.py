import urllib.parse
import requests
import json
import jwt
import io
import os
import base64
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.primitives import hashes
import time
import pathlib
import datetime
import webbrowser
import uuid
import urllib
import struct
import subprocess
from rich import print

from Modules.Settings import Clients, Scopes, Extensions

#https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth-ropc
def ResourceOwnerPasswordCredentials(user, password, tenant, client, scope, usecae, endpointversion, useragent=None):
    response = None
    headers = {}
    endpoint = "v2.0/token"

    try:
        # v2.0 - uses scope instead of resource and include offline_access to include refresh token in response
        # https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth-ropc
        data = {
            "client_id": Clients.GetClientId(client),
            "scope": Scopes.GetScope(scope),
            "username": user,
            "password": password,
            "grant_type": "password"
        }

        if tenant == "common" and user:
            tenant = user.split("@")[1]
        
        if useragent:
            headers.update({"User-Agent": useragent})

        if endpointversion == "1":
            endpoint = "/token"
            data.pop("scope")
            data.update({"resource": f"https://{Scopes.GetScope(scope).split('/')[2]}/"})
        
        if usecae:
            data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})

        # use /oauth2/v2.0/token for newer version of the rest api
        response = requests.post(url=f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

    except Exception as e:
        response = e
    finally:
        return response
    
def ClientSecretCredentials(password, tenant, clientid, scope, usecae, endpointversion, useragent=None):
    response = None
    headers = {}
    endpoint = "v2.0/token"

    try:
        # v2.0 - uses scope instead of resource and include offline_access to include refresh token in response
        # https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#get-a-token
        data = {
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
            "client_secret": password,
            "grant_type": "client_credentials"
        }

        if endpointversion == "1":
            endpoint = "token"
            data.pop("scope")
            data.update({"resource": f"https://{Scopes.GetScope(scope).split('/')[2]}/"})
       
        if usecae:
            data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})

        if useragent:
           headers.update({"User-Agent": useragent})

         # use /oauth2/v2.0/token for newer version of the rest api
        response = requests.post(url=f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

    except Exception as e:
        response = e
    finally:
        return response
    
def DeviceCode(user, password, tenant, clientid, scope, usecae, endpointversion, useragent):

    try:
        # v2.0 - uses scope instead of resource and include offline_access to include refresh token in response
        # https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code
        
        # Device authorization request
        device_auth_response = None
        headers = {}

        device_auth_data = {
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
        }

        if tenant == "common" and user:
            tenant = user.split("@")[1]
        
        if useragent:
            headers.update({"User-Agent": useragent})
     
        device_auth_response = None

        if endpointversion == "1":
            device_auth_response = requests.post(f"https://login.microsoftonline.com/{tenant}/oauth2/devicecode", data=device_auth_data, headers=headers)
        else:
            device_auth_response = requests.post(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/devicecode", data=device_auth_data, headers=headers)

        if device_auth_response.status_code == 200:
            device_auth_response = json.loads(device_auth_response.content.decode("utf-8"))

            print(f"Input this device code into the browser window that will open: [bold blue]{device_auth_response['user_code']}[/bold blue]")
            
            if "verification_uri" in device_auth_response:
                webbrowser.open_new(device_auth_response['verification_uri'])
            elif "verification_url" in device_auth_response:
                webbrowser.open_new(device_auth_response['verification_url'])
            
            counter = 30

            while counter > 0:
                print(f"{counter} seconds remaning...")
                time.sleep(1)
                counter = counter - 1

            # Authenticate user
            response = None
            endpoint = "v2.0/token"

            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": Clients.GetClientId(clientid),
                "device_code": device_auth_response["device_code"]
            }

            if endpointversion == "1":
                endpoint = "token"
                data.pop("device_code")
                data.update({"code": device_auth_response["device_code"]})

            if usecae:
                data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})

            response = requests.post(f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

            if response.status_code != 200:
                response = response.content.decode("utf-8")

    except Exception as e:
        response = e
    finally:
        return response

def AuthorizationCode(user, password, tenant, clientid, scope, usecae, endpointversion, useragent=None):
    resp_code_client = [ 
        "14d82eec-204b-4c2f-b7e8-296a70dab67e",
        "69cc3193-b6c4-4172-98e5-ed0f38ab3ff8",
        "c40dfea8-483f-469b-aafe-642149115b3a",
        "c44b4083-3bb0-49c1-b47d-974e53cbdf3c",
        "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
        "6c7e8096-f593-4d72-807f-a5f86dcc9c77",
        "74658136-14ec-4630-ad9b-26e160ff0fc6"
    ]

    response = None
    headers = {}
    endpoint = "v2.0/token"

    if useragent:
        headers.update({"User-Agent": useragent})

    if tenant == "common" and user != None:
        tenant = user.split("@")[1]

    try:        
        url = None
        #redirectUri = "http://localhost"
        #redirectUri = "http://localhost:8400"
        redirectUri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
        responseType = None

        if endpointversion == "1":
            url = f"https://login.microsoftonline.com/{tenant}/oauth2/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&nonce={uuid.uuid4()}&state={uuid.uuid4()}"
        else:
            # use /oauth2/v2.0/token for newer version of the rest api
            url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&nonce={uuid.uuid4()}&state={uuid.uuid4()}"


        # Adjust redirect uri and response type
        client_guid = Clients.GetClientId(clientid)
        match client_guid:
            case "69cc3193-b6c4-4172-98e5-ed0f38ab3ff8":
                redirectUri = urllib.parse.quote_plus(f"https://intune.microsoft.com")
                # headers.update({"Origin": "https://intune.microsoft.com"})
                # headers.update({"Referer": "https://intune.microsoft.com/"})
            case "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223":
                redirectUri = urllib.parse.quote_plus(f"ms-appx-web://Microsoft.AAD.BrokerPlugin/{client_guid}")
            # case "c44b4083-3bb0-49c1-b47d-974e53cbdf3c":
            #     redirectUri = urllib.parse.quote_plus(r"https://portal.azure.com/")
            #     headers.update({"Referer": "https://portal.azure.com/"})

        if  client_guid in resp_code_client:
            responseType =  "code"
        else:
            responseType =  "code%20id_token"


        url = url + f"&redirect_uri={redirectUri}&response_type={responseType}"
        webbrowser.open_new(url)

        # https://stackoverflow.com/questions/24339236/getting-the-final-redirected-url
        authcode_url = input("Input entire url with authcode here (url in browser navbar on blank page): ")
        
        # v2.0 - uses scope instead of resource and include offline_access to include refresh token in response
        # https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#get-a-token
        data = {
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
            "grant_type": "authorization_code",
            "redirect_uri": redirectUri
        }

        if urllib.parse.urlparse(authcode_url).netloc == "login.microsoftonline.com":
            if authcode_url.find("#") > -1:
                data["code"] = urllib.parse.urlparse(authcode_url).fragment.split("&")[0].split("=")[1]
            else:
                data["code"] = urllib.parse.urlparse(authcode_url).query.split("&")[0].split("=")[1]
        elif urllib.parse.urlparse(authcode_url).netloc == "intune.microsoft.com":
            data["code"] = urllib.parse.urlparse(authcode_url).query.split("&")[0].split("=")[1]

        if endpointversion == "1":
            endpoint = "token"
            data.pop("scope")
            data.update({"resource": f"https://{Scopes.GetScope(scope).split('/')[2]}/"})

        if usecae:
            data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})

        # use /oauth2/v2.0/token for newer version of the rest api
        response = requests.post(url=f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

    except Exception as e:
        response = e
    finally:
        return response
    
def Implicit(user, password, tenant, clientid, scope, usecae, endpointversion, useragent=None):
    response = None
    headers = {}
    endpoint = "v2.0/token"

    if useragent:
        headers.update({"User-Agent": useragent})

    if tenant == "common" and user != None:
        tenant = user.split("@")[1]

    try:        
        url = None
        redirectUri = None
        responseType = None

        if endpointversion == "1":
            url = f"https://login.microsoftonline.com/{tenant}/oauth2/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&nonce={uuid.uuid4()}&state={uuid.uuid4()}"
        else:
            # use /oauth2/v2.0/token for newer version of the rest api
            url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&nonce={uuid.uuid4()}&state={uuid.uuid4()}"
        

        match clientid:
            case "security":
                responseType =  "token+id_token"
                redirectUri = "https://security.microsoft.com"
            case _:
                responseType =  "token+id_token"
                redirectUri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
        
        url = url + f"&redirect_uri={redirectUri}&response_type={responseType}"
        webbrowser.open_new(url)

        # https://stackoverflow.com/questions/24339236/getting-the-final-redirected-url
        authcode_url = input("Input entire url with authcode here (url in browser navbar on blank page): ")

        # v2.0 - uses scope instead of resource and include offline_access to include refresh token in response
        # https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#get-a-token
        # data = {
        #     "client_id": Clients.GetClientId(clientid),
        #     "scope": Scopes.GetScope(scope),
        #     "grant_type": "authorization_code",
        #     "redirect_uri": redirectUri
        # }

        # data["code"] = authcode_url.split("&")[0].split("=")[1]

        # if endpointversion == "1":
        #     endpoint = "token"
        #     data.pop("scope")
        #     data.update({"resource": f"https://{Scopes.GetScope(scope).split('/')[2]}/"})

        # if usecae:
        #     data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})

        # # use /oauth2/v2.0/token for newer version of the rest api
        # response = requests.post(url=f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

    except Exception as e:
        response = e
    finally:
        return response
    
# #https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#second-case-access-token-request-with-a-certificate
# #https://learn.microsoft.com/en-us/entra/identity-platform/certificate-credentials
def MakeAssertion(certificate, password, tenant, clientid, endpointversion):
    pfx_data = certificate.read()
    privatekey = None
    cert = None
    additionalCertificates = None
    thumbprint = None

    if password:
        privatekey, cert, additionalCertificates = load_key_and_certificates(pfx_data, password)
        thumbprint = cert.fingerprint(hashes.SHA1())
    else:
        privatekey, cert, additionalCertificates = load_key_and_certificates(pfx_data, None)
        thumbprint = cert.fingerprint(hashes.SHA1())

    thumbprint = base64.urlsafe_b64encode(thumbprint).decode("utf-8")

    # Header for the JWT
    headers = {
        "alg": "PS256",  # Algorithm used for signing
        "typ": "JWT",     # Token type
        "x5t": thumbprint
    }

    # Payload of the JWT (also called claims)
    endpoint = "v2.0/token"
    if endpointversion == "1":
        endpoint = "token"

    payload = {
        "aud": f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}",# Audience (the API you're authenticating against)
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=960), # Expiration time
        "iss": Clients.GetClientId(clientid),        # Issuer (client_id)
        "jti": "12334434341234",         # JWT ID (unique identifier for the token)
        "nbf": datetime.datetime.now(),
        "sub": Clients.GetClientId(clientid),       # Subject (could be the same as iss)
        "iat": datetime.datetime.now()     # Issued at (current time)
    }

    return jwt.encode(payload, privatekey, algorithm="PS256", headers=headers)

#FIXME: endpoint v1
def CertificateBasedAuthentication(certificate, password, tenant, clientid, scope, usecae, endpointversion, useragent):
    assertion = MakeAssertion(certificate, password, tenant, Clients.GetClientId(clientid), endpointversion)
    response = None
    headers = {}
    endpoint = "v2.0/token"

    if not tenant:
        print("[bold red][!][/bold red]: You must supply a tenant id or alias with --tenant.")

    if useragent:
        headers.update({"User-Agent": useragent})
        
    try:
        data = {
            "tenant": tenant,
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
            "grant_type": "client_credentials"
        }

        if usecae:
            data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})
        
        if useragent:
            headers.update({"User-Agent": useragent})

        if endpointversion == "1":
            endpoint = "token"
            data.pop("scope")
            data.update({"resource": f"https://{Scopes.GetScope(scope).split('/')[2]}/"})
        
        response = requests.get(f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

    except Exception as e:
        response = e
    finally:
        return response

# https://dirkjanm.io/abusing-azure-ad-sso-with-the-primary-refresh-token/
# def PrimaryRefreshToken(tenant):
#     process = subprocess.Popen([r"C:\Windows\BrowserCore\browsercore.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#     inv = {}
#     inv['method'] = 'GetCookies'
#     inv['sender'] = "https://login.microsoftonline.com"
#     inv['uri'] = 'https://login.microsoftonline.com/common/oauth2/authorize?client_id=4345a7b9-9a63-4910-a426-35363201d503&response_mode=form_post&response_type=code+id_token&scope=openid+profile&state=OpenIdConnect.AuthenticationProperties%3dhiUgyLP6LnqNTRRyNpT0W1WGjOO_9hNAUjayiM5WJb0wwdAK0fwF635Dw5XStDKDP9EV_AeGIuWqN_rtyrl8m9t6pUGiXHhG3GMSSpW-AWcpfxW9D6bmWECYrN36_9zw&nonce=636957966885511040.YmI2MDIxNmItZDA0Yy00MjZlLThlYjAtYjNkNDM5NzkwMjVlYThhYTMyZGYtMGVlZi00Mjk4LWE2ODktY2Q2ZjllODU4ZjNk&redirect_uri=https%3a%2f%2fwww.office.com%2f&ui_locales=nl&mkt=nl&client-request-id=d738dfc8-db89-4f27-9522-eb70aa55c2b3&sso_nonce=AQABAAAAAADCoMpjJXrxTq9VG9te-7FX2rBuuPsFpQIW4_wk_IAK5pG2t1EdXLfKDDJotUpwFvQKzd0U_I_IKLw4CEQ5d9uzoWgbWEsY6lt1Tm3Kpw9CfiAA'
#     text = json.dumps(inv).encode('utf-8')
#     encoded_length = struct.pack('=I', len(text))
#     print(process.communicate(input=encoded_length + text)[0])   


def Refresh(refreshtoken, tenant, clientid, scope, usecae, endpointversion, useragent):
    response = None
    headers = {}
    endpoint = "v2.0/token"

    # brkids = [
    #     # Bitlocker read and device local credential read permissions
    #     "c40dfea8-483f-469b-aafe-642149115b3a", # Microsoft_AAD_Devices
    #     "aad devices",
    #     # Cloud PC read & write, Device configuration managment read permissons
    #     "69cc3193-b6c4-4172-98e5-ed0f38ab3ff8",
    #     "cloud pc",
    #     # Cloud PC read & write, Device configuration managment read/write, device app management read/write, device management devices privileged operations, service configuration read/write, sites read permissons
    #     "5926fc8e-304e-4f59-8bed-58ca97cc39a4", # Microsoft_Intune, Microsoft_Intune_Devices
    #     "intune portal extension",
    #     "74658136-14ec-4630-ad9b-26e160ff0fc6", # Microsoft_AAD_IAM
    #     "adibizaux",
    #     "c44b4083-3bb0-49c1-b47d-974e53cbdf3c",
    #     "azure portal",
    # ]

    ext_ids = [
        "c40dfea8-483f-469b-aafe-642149115b3a",
        "5926fc8e-304e-4f59-8bed-58ca97cc39a4",
        "74658136-14ec-4630-ad9b-26e160ff0fc6"
    ]
    
    try:
        data = {
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
            "grant_type": "refresh_token",
            "refresh_token": refreshtoken
        }

        # Check if client id is extension and add post args and headers needed
        if Clients.GetClientId(clientid) in ext_ids:
            data["brk_client_id"] = "c44b4083-3bb0-49c1-b47d-974e53cbdf3c"
            data['redirect_uri'] ="brk-c44b4083-3bb0-49c1-b47d-974e53cbdf3c://intune.microsoft.com"
            headers.update({"Origin": "https://portal.azure.com/"})
            headers.update({"Referer": "https://portal.azure.com/"})

        if usecae:
            data["claims"] = json.dumps({"access_token":{"xms_cc":{"values":["CP1"]}}})
        
        if useragent:
            headers.update({"User-Agent": useragent})
        
        if endpointversion == "1":
            endpoint = "token"
            data.pop("scope")
            data.update({"resource": f"https://{Scopes.GetScope(scope).split('/')[2]}/"})
        
        response = requests.get(f"https://login.microsoftonline.com/{tenant}/oauth2/{endpoint}", data=data, headers=headers)

    except Exception as e:
        response = e
    finally:
        return response

# https://github.com/secureworks/family-of-client-ids-research?tab=readme-ov-file#example-2---decode-access-token
def Decode(accesstoken):
    token_data = jwt.decode(accesstoken, options={"verify_signature": False, "verify_aud": False})
    return token_data

# Updated reference from https://github.com/Gerenios/AADInternals/blob/9c8fd15d2a853a6d6515da15d0d81bd3e0475f6d/AzureManagementAPI_utils.ps1#L461
def DelegationToken(authInfo, extension, resource):
    response = None

    try:
        body = {
            "extensionName": Extensions.GetExtension(extension)["name"],
            "resourceName": resource,
            "tenant": authInfo["user"]["tenantId"],
            "portalAuthorization": authInfo["refreshToken"],
            "altPortalAuthorization": authInfo["altRefreshToken"]
        }

        headers = {
            "x-ms-client-request-id": str(uuid.uuid4()),
            "x-ms-extension-flags": '{"feature.advisornotificationdays":"30","feature.advisornotificationpercent":"100","feature.armtenants":"true","feature.artbrowse":"true","feature.azureconsole":"true","feature.checksdkversion":"true","feature.contactinfo":"true","feature.dashboardfilters":"false","feature.enableappinsightsmetricsblade":"true","feature.globalsearch":"true","feature.guidedtour":"true","feature.helpcontentenabled":"true","feature.helpcontentwhatsnewenabled":"true","feature.internalonly":"false","feature.irissurfacename":"AzurePortal_Notifications_PROD","feature.mergecoadmins":"true","feature.metricsv2ga":"true","feature.newsubsapi":"true","feature.npsintervaldays":"90","feature.npspercent":"3.0","feature.npsshowportaluri":"true","feature.sessionvalidity":"true","feature.searchnocache":"true","feature.subscreditcheck":"true","hubsextension_parameterseditor":"true","hubsextension_showpolicyhub":"true","feature.autosettings":"true","feature.azurehealth":"true","feature.blockbladeredirect":"Microsoft_Azure_Resources","feature.browsecuration":"default","feature.collapseblade":"true","feature.dashboardfiltersaddbutton":"false","feature.decouplesubs":"true","feature.disablebladecustomization":"true","feature.disabledextensionredirects":"","feature.enablee2emonitoring":"true","feature.enablemonitoringgroup":"true","feature.enableworkbooks":"true","feature.feedback":"true","feature.feedbackwithsupport":"true","feature.fullwidth":"true","feature.managevminbrowse":"true","feature.mgsubs":"true","feature.newautoscale":"true","feature.newtageditorblade":"true","feature.nps":"true","feature.pinnable_default_off":"true","feature.reservationsinbrowse":"true","feature.reservehozscroll":"true","feature.resourcehealth":"true","feature.seetemplate":"true","feature.showdecoupleinfobox":"true","feature.tokencaching":"true","feature.usealertsv2blade":"true","feature.usemdmforsql":"true","feature.usesimpleavatarmenu":"true","hubsextension_budgets":"true","hubsextension_costalerts":"false","hubsextension_costanalysis":"true","hubsextension_costrecommendations":"true","hubsextension_eventgrid":"true","hubsextension_isinsightsextensionavailable":"true","hubsextension_islogsbladeavailable":"true","hubsextension_isomsextensionavailable":"true","hubsextension_savetotemplatehub":"true","hubsextension_servicenotificationsblade":"true","hubsextension_showservicehealthevents":"true","microsoft_azure_marketplace_itemhidekey":"Citrix_XenDesktop_EssentialsHidden,Citrix_XenApp_EssentialsHidden,AzureProject"}',
            "x-ms-version": authInfo['x-ms-version'],
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://{authInfo['domain']}/",
            "x-ms-client-session-id": authInfo["aadSessionId"],
            "Origin": f"https://{authInfo['domain']}",
            "x-ms-effective-locale": "en.en-us",
            "Accept-Language": "en",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Cookie": f"portalId={authInfo['portalId']}",
            #"Cookie": f"browserId={str(uuid.uuid4())}", # older version of this endpoint required this cookie; replaced with portalId (get value from kmsi auth flow)
            "Content-Type": "application/json"
        }

        response = requests.post(f"https://{authInfo['domain']}/api/DelegationToken?feature.tokencaching=true", headers=headers, json=body)

        if response.status_code == 200:
            tokens = json.loads(response.content.decode("utf-8"))

            if "value" in tokens:
                response = tokens
        else:
            response = "[bold red][-][/bold red] Could not obtain token!"
    except Exception as e:
        response = e
    finally:
        return response

def SubmitSPACode(spacode, tenant, domain):
    response = None

    try:
        body = {
            "client_id": Clients.GetClientId("azure portal"),
            "code": spacode,
            "scope": urllib.parse.quote("openid profile offline_access"),
            "grant_type": "authorization_code"
        }

        headers = {
            "Origin": f"https://{domain}"
        }

        response = requests.post(url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token", headers=headers, data=body)

        if response.status_code == 200:
            response = json.loads(response.content.decode("utf-8"))

    except Exception as e:
        response = e
    finally:
        return response

def SaveToken(tokens, user, password, client, scope):
    
    tokens["username"] = user
    tokens["password"] = password
    tokens["client"] = client
    tokens["scope"] = scope

    dir = f"{os.path.dirname(os.path.abspath(__file__))}/../Loot/Tokens/"

    tokenfile = None
    tokendata = None

    try:
        if os.path.exists(f"{dir}tokencache.json"):
            if os.stat(f"{dir}tokencache.json").st_size <= 0:
                tokendata = {"tokens":[]}
            else:
                tokenfile = io.open(f"{dir}tokencache.json", "r+")
                tokendata = json.loads(tokenfile.read())
                tokenfile.close()
        else:
            pathlib.Path(f"{dir}").mkdir(parents=True, exist_ok=True)
            tokendata = {"tokens":[]}
        
        with io.open(f"{dir}tokencache.json", "w+") as tokenfile:
            tokendata["tokens"].append(tokens) 
            tokenfile.write(json.dumps(tokendata))
        
        
    except Exception as e:
        print(e)
    finally:
        pass

def ListToken():
    dir = f"{os.path.dirname(os.path.abspath(__file__))}/../Loot/Tokens/"

    tokenfile = None
    tokendata = None

    try:
        if os.path.exists(f"{dir}tokencache.json"):
            if os.stat(f"{dir}tokencache.json").st_size > 0:
                tokenfile = io.open(f"{dir}tokencache.json", "r+")
                tokendata = json.loads(tokenfile.read())
                tokenfile.close()
            else:
                response = "No tokens found!"
        else:
            response = "No tokens found!"

        
        response = tokendata
        
    except Exception as e:
        response = e
    finally:
        return response