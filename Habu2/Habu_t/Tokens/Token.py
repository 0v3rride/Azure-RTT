import requests
import json
import jwt
import io
import os
import base64
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.primitives import hashes, serialization
import time
import pathlib
import datetime
import webbrowser
from rich import print

from Modules.Settings import Clients, Scopes

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

        if tenant == None:
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

        if tenant == None:
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
    response = None
    headers = {}
    endpoint = "v2.0/token"

    if useragent:
           headers.update({"User-Agent": useragent})

    if tenant == None:
        if user:
            tenant = user.split("@")[1]

    try:
        headers = {}

        if tenant == None:
            tenant = user.split("@")[1]

        # use /oauth2/v2.0/token for newer version of the rest api
        #webbrowser.open_new(url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&response_type=code&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&")
        if endpointversion == "1":
            webbrowser.open_new(f"https://login.microsoftonline.com/{tenant}/oauth2/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&response_type=code&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient")
        else:
            webbrowser.open_new(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?client_id={Clients.GetClientId(clientid)}&scope={Scopes.GetScope(scope)}&domain_hint={tenant}&login_hint={user}&response_type=code&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient")
        
        # https://stackoverflow.com/questions/24339236/getting-the-final-redirected-url
        authcode_url = input("Input entire url with authcode here (url in browser navbar on blank page): ")

        # v2.0 - uses scope instead of resource and include offline_access to include refresh token in response
        # https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#get-a-token
        data = {
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
            "grant_type": "authorization_code",
            "redirect_uri": "https://login.microsoftonline.com/common/oauth2/nativeclient"
        }

        data["code"] = authcode_url.split("&")[0].split("=")[1]

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


def Refresh(refreshtoken, tenant, clientid, scope, usecae, endpointversion, useragent):
    response = None
    headers = {}
    endpoint = "v2.0/token"

    try:
        data = {
            "client_id": Clients.GetClientId(clientid),
            "scope": Scopes.GetScope(scope),
            "grant_type": "refresh_token",
            "refresh_token": refreshtoken
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

# https://github.com/secureworks/family-of-client-ids-research?tab=readme-ov-file#example-2---decode-access-token
def Decode(accesstoken):
    token_data = jwt.decode(accesstoken, options={"verify_signature": False, "verify_aud": False})
    return token_data


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
        
    

    
    
    
