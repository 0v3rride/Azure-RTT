import requests
import json
import uuid
import re
import urllib.parse
import xmltodict

# import Modules.Settings.Portals

# https://github.com/silverhack/donkeytoken/tree/99cba6f27a93c0599e57dc5947fc4a70896891a7
# https://github.com/Gerenios/AADInternals/blob/9c8fd15d2a853a6d6515da15d0d81bd3e0475f6d/AzureManagementAPI_utils.ps1#L133
# https://github.com/Mayyhem/Maestro/blob/main/source/authentication

session = requests.Session()

def _set_cookies(session, cookies):
    for cookie in cookies:
        session.cookies.set(cookie.name, cookie.value)

def _auth_login_msonline(username, password, tenant, config, userinfo):
    bypass_config = None
    raw_login = None

    if userinfo and config:
        body = {
            "login": username,
            "loginFmt": username,
            "i13":"0",
            "type":"11",
            "LoginOptions":"3",
            "passwd":password,
            "ps":"2",
            "flowToken":userinfo["FlowToken"],
            "canary":config["canary"],
            "ctx":config["sCtx"],
            "NewUser":"1",
            "PPSX":"",
            "fspost":"0",
            "hpgrequestid":str(uuid.uuid4())
        }

        headers = {
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://login.microsoftonline.com/"
        }

        msonline_url = None

        if tenant == None:
            msonline_url = "https://login.microsoftonline.com/common/login"
        else:
            msonline_url = f"https://login.microsoftonline.com/{tenant}/login"
        
        response = session.post(msonline_url, data=body, headers=headers)
        
        if response.status_code == 200:
            location = response.headers.get("Location")

            if location:
                if location.find("device.login.microsoftonline.com") > -1:
                    pass
                    # Write-Verbose "device login detected"
                    # $raw_login = Connect-MsDeviceLogin -Url $location
                    # $raw_response.Close()
                    # $raw_response.Dispose()
                elif location.find("#code") > -1:
                    pass
                    # Write-Verbose "Code detected"
                    # $bypassConfig = $True
                    # $config = $location
                    # #Close request
                    # $raw_response.Close()
                    # $raw_response.Dispose()
            else:
                raw_login = response.content.decode("utf-8")
            
            if not bypass_config:
                config = json.loads(re.search('{.*}', raw_login, re.IGNORECASE).group(0))
            
        if config:
            return config

def _auth_adfs(adfsurl, username, password, userinfo):
    login_srf_info = {
        "hidden_form": None,
        "wa": None,
        "wresult": None,
        "wctx": None
    }

    adfshtml = None

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        #"Referer": urllib.parse.unquote(adfsurl) #leading whitespace error
    }

    body = {
        "UserName": username,
        "Password": password
    }

    adfssession = requests.Session()

    response = session.post(url=adfsurl, headers=headers, data=body)
    # _set_cookies(adfssession, response.cookies)
    
    if response.status_code == 200:
        html = xmltodict.parse(response.text)

        login_srf_info["hidden_form"] = html["html"]["body"]["form"]["@action"]
        forminfo = html["html"]["body"]["form"]["input"]

        for formitem in forminfo:
            match formitem["@name"]:
                case "wa":
                    login_srf_info['wa'] = formitem["@value"]
                case "wresult":
                    login_srf_info['wresult'] = formitem["@value"]
                case "wctx":
                    login_srf_info['wctx'] = f"LoginOptions=3&{formitem['@value'].rstrip(' ')}"
        
        if all(login_srf_info.values()):
            body = login_srf_info.copy()
            body.pop("hidden_form")

            adfssession.cookies.set("ESTSWCTXFLOWTOKEN", userinfo["FlowToken"]) # or config['sFT']
            adfssession.cookies.set("esctx", session.cookies.get("esctx"))
            adfssession.cookies.set("x-ms-gateway-slice", "estsfd")
            adfssession.cookies.set("stsservicecookie", "estsfd")
            adfssession.cookies.set("AADSSO", "NA|NoExtension")
            adfssession.cookies.set("fpc", session.cookies.get('fpc'))

            response = adfssession.post(url=login_srf_info["hidden_form"], headers=headers, data=body, allow_redirects=False)

            if response.status_code == 200:
                adfshtml = response.content.decode("utf-8")
            
            return adfshtml  

def _get_kmsi_flow(config, userinfo, username, password):
    body = None
    kmsiurl = "https://login.microsoftonline.com/kmsi"
    auth_flow = {}
    html = None
    adfshtml = None

    headers = {
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://login.microsoftonline.com/common/login"
    }

    if "sFT" in config and 'canary' in config and 'sCtx' in config:
        body = {
            "LoginOptions":"0",
            "flowToken":config['sFT'],
            "canary":config['canary'],
            "ctx":config['sCtx'], 
            "hpgrequestid": str(uuid.uuid4())
        }

        try:
            response = session.post(kmsiurl, headers=headers, data=body)

            if response.status_code == 200:
                adfsurl = re.search("https:\/\/.*\/adfs\/.*", response.text, re.IGNORECASE)
                
                if adfsurl:
                    adfsurl = adfsurl.group(0).replace("\">", "")
                    adfshtml = _auth_adfs(adfsurl, username, password, userinfo)
                
                if adfshtml:
                    html = xmltodict.parse(adfshtml)
                else:
                    html = xmltodict.parse(response.text)

                auth_flow.update({"hidden_form": html["html"]["body"]["form"]["@action"]})
                forminfo = html["html"]["body"]["form"]["input"]

                for formitem in forminfo:
                    match formitem["@name"]:
                        case "code":
                            auth_flow.update({"code": formitem["@value"]})
                        case "id_token":
                            auth_flow.update({'id_token': formitem["@value"]})
                        case "state":
                            auth_flow.update({"state": formitem["@value"]})
                        case "session_state":
                            auth_flow.update({'session_state': formitem["@value"]})

            if all(auth_flow.values()):
                return auth_flow
        except Exception as e:
            response = "[bold red][-][/bold red] Unable to get authentication flow!"
    elif "unsafe_strTopMessage" in config:
        print("[bold red][-][/bold red]: unsafe_strTopMessage")

def login(username, password, tenant, portal):
    url = None
    portal_url = None

    match portal:
        case "azure":
            url = "https://portal.azure.com/signin/idpRedirect.js/"
            portal_url = "https://portal.azure.com/signin/index/"
        case "intune":
            url = "https://intune.microsoft.com/signin/idpRedirect.js/"
            portal_url = "https://intune.mcirosoft.com/signin/index/"
        case "security":
            url = "https://security.microsoft.com/"

    config = None
    login_msonline_url = None
    response = None

    try:
        if tenant == None and username:
            tenant = username.split("@")[1]
        
        # First request to get login url and cookies for flow
        if portal == "security":
            response = session.get(url=url, allow_redirects=False)
            _set_cookies(session, response.cookies)
            login_msonline_url = response.headers.get("Location")
        else:
            session.cookies.set("browserId", str(uuid.uuid4()))

            response = session.get(url=url)
            _set_cookies(session, response.cookies)
            login_msonline_url = re.search("https://login.microsoftonline.com.*[^\");]", response.text, re.IGNORECASE).group(0)

        # Second request get credential type url
        session.cookies.set("x-ms-gateway-slice", "004")
        session.cookies.set("stsservicecookie", "ests")
        session.cookies.set("AADSSO", "NANoExtension")
        session.cookies.set("SSOCOOKIEPULLED", "1")

        response = session.get(url=login_msonline_url)
        config = json.loads(re.search('{.*}', response.text, re.IGNORECASE).group(0))
        credential_type_url = config["urlGetCredentialType"]

        body = {}
        if "sFT" in config:
            body["flowToken"] = config["sFT"]
            body["username"] = username
        
        # Third Request get user info for login
        response = requests.post(credential_type_url, headers={"Content-Type": "application/json; charset=UTF-8"}, json=body)
        user_info = json.loads(response.content.decode("utf-8"))

        if isinstance(user_info, dict):
            # Fourth request auth to portal and get kmsi url in flow
            config = _auth_login_msonline(username, password, tenant, config, user_info)

            if config and ("sFT" in config and 'canary' in config and 'sCtx' in config): 
                # Fifth request complete kmsi and get next url in flow
                flow_auth = _get_kmsi_flow(config, user_info, username, password)

                if isinstance(flow_auth, dict):
                    #auth_response = None
                    body = flow_auth.copy()
                    body.pop("hidden_form")

                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": "https://login.microsoftonline.com/"
                    }

                    # Sixth request get oauth tokens
                    response = session.post(url=flow_auth["hidden_form"], data=body, headers=headers, allow_redirects=False)
                    
                    if response.status_code == 200:
                        auth_response = json.loads(re.search('{\"oAuthToken.*}', response.text, re.IGNORECASE).group(0))
                        auth_response.update({"portalId": response.cookies.get("portalId")})
                        auth_response.update({"x-ms-version": response.headers.get('x-ms-version')})
                        auth_response.update({"domain": urllib.parse.urlsplit(auth_response['user']['defaultAvatarUri']).netloc})
                        response = auth_response
                    elif response.status_code == 302 and portal == "security":
                        security_tokens = {
                            "sccauth": response.cookies.get("sccauth"),
                            "x-xsrf-token": None
                        }

                        if security_tokens["sccauth"]:
                            securitySession = requests.Session()
                            securitySession.cookies.set("sccauth", security_tokens["sccauth"])
                            securitySession.cookies.set("s.SessID", session.cookies.get_dict()['s.SessID'])
                            securitySession.cookies.set("X-PortalEndpoint-RouteKey", session.cookies.get_dict()["X-PortalEndpoint-RouteKey"])

                            response = securitySession.get(url=url)

                            if response.status_code == 200:
                                security_tokens["x-xsrf-token"] = urllib.parse.unquote(response.cookies.get("XSRF-TOKEN"))
                            
                            response = security_tokens
        else:
            response = "[bold red][-][/bold red] Could not get user info!"
    except Exception as e:
        response = e
    finally:
        return response