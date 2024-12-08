import typer
from typing_extensions import Annotated
from rich import print
from rich.console import Console
from rich.table import Table
import os
import json
import azure.identity
import requests

from Modules.Settings import GrantType, Extensions, Portals
from Modules.Credential import Spray
import Modules.Settings.Clients
import Modules.Settings.Scopes
import Authentication.Token
import Authentication.Selenium
import Authentication.Portal
import Modules.Settings
from Modules.Entra import Users, Roles, AdministrativeUnits, Groups, Policies, Apps, ServicePrincipals, Objects
from Modules.O365 import Teams, Exchange, OneDrive, OneNote, SharePoint, Substrate
from Modules.ARM import Storage, SQL, KeyVault, Resources, Subscriptions, RBACRoles, KuduAPI, VM, PublicIPAddress
from Modules.Security import ThreatHunting, LiveResponse
from Modules.Intune import Intune
from Modules.ARM.AppService import WebApp, FunctionApp
from Modules.Enumeration import Tenant


root_dir = os.path.dirname(os.path.abspath(__file__))
error_console = Console(stderr=True)

# Init Main app
app = typer.Typer(help=".\habu2.py <action> <service> <item> <options/flags>")

# Init Verbs
get_app = typer.Typer()
app.add_typer(get_app, name="get")
update_app = typer.Typer()
app.add_typer(update_app, name="update")
add_app = typer.Typer()
app.add_typer(add_app, name="add")
remove_app = typer.Typer()
app.add_typer(remove_app, name="remove")

# Tokens
refresh_app = typer.Typer()
app.add_typer(refresh_app, name="refresh")
decode_app = typer.Typer()
app.add_typer(decode_app, name="decode")

# Storage
brute_app = typer.Typer()
app.add_typer(brute_app, name="brute")
list_app = typer.Typer()
app.add_typer(list_app, name="list")

# Substrate
substrate_app = typer.Typer()

# Kuduapi
cmd_app = typer.Typer()
app.add_typer(cmd_app, name="cmd")

# Sql
connect_app = typer.Typer()
app.add_typer(connect_app, name="connect")

# Security
query_app = typer.Typer()
app.add_typer(query_app, name="query")


# Init services app
entra_app = typer.Typer(name="entra_app")
rbacrole_app = typer.Typer(name="rbacrole_app")
functionapp_app = typer.Typer(name="functionapp_app")
webapp_app = typer.Typer(name="webapp_app")
kuduapi_app = typer.Typer(name="kuduapi_app")
keyvault_app = typer.Typer(name="keyvault_app")
subscriptions_app = typer.Typer(name="subscriptions_app")
resources_app = typer.Typer(name="resources_app")
storage_app = typer.Typer(name="storage_app")
vm_app = typer.Typer(name="vm_app")
onenote_app = typer.Typer(name="onenote_app")
onedrive_app = typer.Typer(name="onedrive_app")
teams_app = typer.Typer(name="teams_app")
sharepoint_app = typer.Typer(name="sharepoint_app")
exchange_app = typer.Typer(name="exchange_app")
substrate_app = typer.Typer(name="substrate_app")

# Init special services apps
security_app = typer.Typer(name="security_app")
intune_app = typer.Typer(name="intune_app")
token_app = typer.Typer(name="token_app")
delegationtoken_app = typer.Typer(name="delegation-token_app")
spray_app = typer.Typer(name="spray_app")
tenant_app = typer.Typer(name="tenant_app")
sql_app = typer.Typer(name="sql_app")

init_services = [entra_app, rbacrole_app, subscriptions_app, resources_app, webapp_app, functionapp_app, webapp_app, keyvault_app, storage_app, vm_app, onenote_app, onedrive_app, teams_app, sharepoint_app, exchange_app, substrate_app]

# Verbs
[get_app.add_typer(service, name=service.info.name.split("_")[0]) for service in init_services]
[get_app.add_typer(service, name=service.info.name.split("_")[0]) for service in [tenant_app, intune_app, delegationtoken_app]]

[add_app.add_typer(service, name=service.info.name.split("_")[0]) for service in init_services]
[update_app.add_typer(service, name=service.info.name.split("_")[0]) for service in init_services]
[remove_app.add_typer(service, name=service.info.name.split("_")[0]) for service in init_services]


# Misc
@tenant_app.command("domains")
def tenant_domains(
    tenant: Annotated[str, typer.Option(help="Tenant id or alias")],
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):

  response = None

  response = Tenant.GetTenantRegisteredDomains(tenant, useragent)

  if isinstance(response, dict):
    if rich:
        pass
    else:
        print(response)

# FIXME: later try to get better output formatting and coloring and show tokens
@app.command(help="Spray credentials and check for MFA gaps in services.")
def spray(
    userlist: Annotated[typer.FileText, typer.Option(help="Path to file containing a list of usernames that is newline separated (use upn format if not providing tenant id/alias).")],
    passwordlist: Annotated[typer.FileText, typer.Option(help="Path to file containing a list of passwords that is newline separated.")],
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")] = "common",
    client: Annotated[str, typer.Option(help="The client id of the app to use to authenticate against.")] = "office",
    scope: Annotated[str, typer.Option(help="Resources/scopes to request the token for.")] = "graph",
    # granttype: Annotated[GrantType.GrantType, typer.Option(help="OAuth flow to use to get token.")] = GrantType.GrantType.ropc,
    usecae: Annotated[bool, typer.Option(help="Add CAE claim to new token.")] = False,
    endpointversion: Annotated[str, typer.Option(help="Oauth endpoint version to use. Use 1 if you're having issues retrieving a refresh token on the newer version.")] = "2",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    mfacheck: Annotated[bool, typer.Option(help="Check which services have MFA enabled if a valid set of credentials are found.")] = False,
    savetokens: Annotated[bool, typer.Option(help="Save token data to ../Loot/Tokens/tokencache.json.")] = False,
    # rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    Spray.main(userlist, passwordlist, tenant, client, scope, usecae, endpointversion, useragent, mfacheck, savetokens)


# Tokens
@get_app.command("token")
def token_get(
    user: Annotated[str, typer.Option(help="Username (use upn format if not providing tenant id/alias).")] = None,
    password: Annotated[str, typer.Option(help="Password for user or client secret.")] = None,
    certificate: Annotated[typer.FileBinaryRead, typer.Option(help="File path to .pfx.")] = None,
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")] = "common",
    client: Annotated[str, typer.Option(help="The client id of the app to use to authenticate against.")] = "office",
    scope: Annotated[str, typer.Option(help="Resources/scopes to request the token for.")] = "graph",
    granttype: Annotated[GrantType.GrantType, typer.Option(help="OAuth flow to use to get token.")] = GrantType.GrantType.ropc,
    #https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
    #https://cloudbrothers.info/en/continuous-access-evaluation/
    #https://github.com/f-bader/TokenTacticsV2/blame/main/modules/TokenHandler.ps1#L164
    usecae: Annotated[bool, typer.Option(help="Add CAE claim to new token.")] = False,
    #https://stackoverflow.com/questions/74730826/using-v2-token-endpoint-still-giving-v1-token-azure-active-directory
    #https://stackoverflow.com/questions/61692247/oauth-2-0-token-end-points
    #https://www.outsystems.com/forums/discussion/92808/azure-ad-login-connector-oauth2-versus-oauth2-v2-0-token-id/
    #https://learn.microsoft.com/en-us/answers/questions/815207/what-do-each-of-the-azure-app-registration-endpoin
    endpointversion: Annotated[str, typer.Option(help="Oauth endpoint version to use. Use 1 if you're having issues retrieving a refresh token on the newer version.")] = "2",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    match granttype.value:
        case "ropc":
            response = Authentication.Token.ResourceOwnerPasswordCredentials(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "clientsecret":
            response = Authentication.Token.ClientSecretCredentials(password, tenant, client, scope, usecae, endpointversion, useragent)
        case "devicecode":
            response = Authentication.Token.DeviceCode(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "authcode":
            response = Authentication.Token.AuthorizationCode(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "certificate":
            response = Authentication.Token.CertificateBasedAuthentication(certificate, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "implicit":
            response = Authentication.Token.Implicit(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "interactive":
            if tenant == None:
                tenant = user.split("@")[1]

            # https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python
            credential = azure.identity.InteractiveBrowserCredential(tenant_id=tenant, login_hint=user, client_id=Modules.Settings.Clients.GetClientId(client))
            response = credential.get_token(Modules.Settings.Scopes.GetScope(scope))
    
    if rich:
        pass
    else:
        try:
            if isinstance(response, tuple):
                print({"access_token": response.token})
            elif isinstance(response, requests.Response):
                print(json.loads(response.content.decode("utf-8")))
            else:
                print(response)
        except:
            pass

@delegationtoken_app.command("selenium")
def delegation_token_get_selenium(
    user: Annotated[str, typer.Option(help="Username (use upn format if not providing tenant id/alias).")],
    password: Annotated[str, typer.Option(help="Password for user or client secret.")],
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")] = "common",
    extension: Annotated[str, typer.Option(help="""Extension name.
    | aad_devices - gives permission for DeviceLocalCredential.Read.All and BitlockerKey.Read.All
    | intune - gives permission for CloudPC.ReadWrite.All, DeviceManagementApps.ReadWrite.All, DeviceManagementManagedDevices.PrivilegedOperations.All, etc.
    | aad_iam - gives permission for much more related to identity management
                                                           """)] = "aad_devices",         
    scope: Annotated[str, typer.Option(help="Resources/scopes to request the token for.")] = "graph",
    portal: Annotated[Portals.Portal, typer.Option(help="OAuth flow to use to get token.")] = Portals.Portal.azure,
    usecae: Annotated[bool, typer.Option(help="Add CAE claim to new token.")] = False,
    endpointversion: Annotated[str, typer.Option(help="Oauth endpoint version to use. Use 1 if you're having issues retrieving a refresh token on the newer version.")] = "2",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if tenant == "common" and user:
        tenant = user.split("@")[1]

    response = Authentication.Selenium.main(user, password, portal)
    portalrt = None

    if isinstance(response, dict):
        portalrt = response["portal_refresh_token"]
        response = Authentication.Token.Refresh(portalrt, tenant, Extensions.GetExtension(extension)["id"], scope, usecae, endpointversion, useragent)

    if rich:
        pass
    else:
        try:
            if response.status_code == 200:
                print(json.loads(response.content.decode("utf-8")))
            else:
                print(response)
        except:
            pass

@delegationtoken_app.command("authflow")
def delegation_token_get_authflow(
    user: Annotated[str, typer.Option(help="Username (use upn format if not providing tenant id/alias).")] = None,
    password: Annotated[str, typer.Option(help="Password for user or client secret.")] = None,
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")] = "common",
    extension: Annotated[str, typer.Option(help="""Extension name.
    | aad_devices - gives permission for DeviceLocalCredential.Read.All and BitlockerKey.Read.All
    | intune - gives permission for CloudPC.ReadWrite.All, DeviceManagementApps.ReadWrite.All, DeviceManagementManagedDevices.PrivilegedOperations.All, etc.
    | aad_iam - gives permission for much more related to identity management
                                                           """)] = "aad_devices",
    portal: Annotated[Portals.Portal, typer.Option(help="OAuth flow to use to get token.")] = Portals.Portal.azure,
    resource: Annotated[str, typer.Option(help="Resource name (not the same as scope)")] = "microsoft.graph",            
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if tenant == "common" and user:
        tenant = user.split("@")[1]

    response = Authentication.Portal.login(user, password, tenant, portal)

    # Call to intune delegation api endpoint else use spa auth code. Both with retrieve a refresh token with brk_client_id which is needed for the intune extensions (microsoft_aad_iam, microsoft_aad_devices, etc.)
    if portal != "security":
        authData = response
        print(authData)
        response = Authentication.Token.DelegationToken(authData, extension, resource)

        if not isinstance(response, dict):
            response = Authentication.Token.SubmitSPACode(authData["spaAuthCode"], authData["user"]["tenantId"], authData["domain"])
    
    if rich:
        pass
    else:
        try:
            print(response)
        except:
            pass

@refresh_app.command("token")
def token_refresh(
    refreshtoken: Annotated[str, typer.Option(help="Refresh token.")],
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")],
    client: Annotated[str, typer.Option(help="The client id of the app to use to authenticate against.")] = "office",
    scope: Annotated[str, typer.Option(help="Resources/scopes to request the token for.")] = "graph",
    # https://learn.microsoft.com/en-us/entra/identity-platform/claims-challenge?tabs=dotnet
    # https://cloudbrothers.info/en/continuous-access-evaluation/
    # https://github.com/f-bader/TokenTacticsV2/blob/b7b265efaf55bade328fca0f541e0e89c7e53cfb/modules/TokenHandler.ps1#L1019
    usecae: Annotated[bool, typer.Option(help="Add CAE claim to new token.")] = False, 
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    endpointversion: Annotated[str, typer.Option(help="Oauth endpoint version to use. Use 1 if you're having issues retrieving a refresh token on the newer version.")] = "2",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    response = Authentication.Token.Refresh(refreshtoken, tenant, client, scope, usecae, endpointversion, useragent)

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))

@decode_app.command("token")
def token_decode(
    accesstoken: Annotated[str, typer.Option(help="Refresh token.")]
):
    print(Authentication.Token.Decode(accesstoken))


# Entra
@entra_app.command("user")
def entra_user(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    id: Annotated[str, typer.Option(help="User object id or upn.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $select=userprincipalname,id,customsecurityattributes&$top=10) - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if id:
        response = Users.GetUser(accesstoken, id, params, useragent)
    else:
        response = Users.GetAllUsers(accesstoken, params, useragent)

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))

@entra_app.command("adminunit")
def entra_administrativeunit(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    #id: Annotated[str, typer.Option(help="Unit id.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $filter=startsWith(displayName, 'keyword')&$select=displayName,id,description - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    # if id:
    #     response = AdministrativeUnits.GetAdministrativeUnit(accesstoken, unitid, params, useragent)
    # else:
    response = AdministrativeUnits.GetAllAdministrativeUnits(accesstoken, params, useragent)

    if rich:
        pass
    else:
        # If you see missing scopedMembers or members then you're probably being rate limited by some other asshat
        if isinstance(response, list):
            print(response)
        else:
            print(response)

@entra_app.command("serviceprincipal")
def entra_serviceprincipal(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    id: Annotated[str, typer.Option(help="Service principal id.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $select=id,displayname&$top=10) - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if id:
        response = ServicePrincipals.GetServicePrincipal(accesstoken, id, params, useragent)
    else:
        response = ServicePrincipals.GetAllServicePrincipals(accesstoken, params, useragent)

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))

@entra_app.command("role")
def entra_role(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    #id: Annotated[str, typer.Option(help="Unit id.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $filter=startsWith(displayName, 'keyword')&$select=displayName,id,description - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    # if id:
    #     response = AdministrativeUnits.GetAdministrativeUnit(accesstoken, unitid, params, useragent)
    # else:
    response = Roles.GetAllDirectoryRoles(accesstoken, params, useragent)

    if rich:
        pass
    else:
        # If you see missing scopedMembers or members then you're probably being rate limited by some other asshat
        if isinstance(response, list):
            print(response)
        else:
            print(response)

@entra_app.command("group")
def entra_group(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    #id: Annotated[str, typer.Option(help="Unit id.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $filter=startsWith(displayName, 'keyword')&$select=displayName,id,description - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    # if id:
    #     response = AdministrativeUnits.GetAdministrativeUnit(accesstoken, unitid, params, useragent)
    # else:
    response = Groups.GetAllGroups(accesstoken, params, useragent)

    if rich:
        pass
    else:
        # If you see missing scopedMembers or members then you're probably being rate limited by some other asshat
        if isinstance(response, list):
            print(response)
        else:
            print(response)

@entra_app.command("object")
def entraobject_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    userid: Annotated[str, typer.Option(help="User object id or upn.")] = None,
    serviceprincipalid: Annotated[str, typer.Option(help="Service principal id.")] = None,
    appid: Annotated[str, typer.Option(help="Application id.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $select=userprincipalname,id,customsecurityattributes&$top=10) - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if userid:
        response = Objects.GetUserOwnedObject(accesstoken, "users", userid, params, useragent)
    elif serviceprincipalid:
        response = Objects.GetUserOwnedObject(accesstoken, "servicePrincipals", serviceprincipalid, params, useragent)
    elif appid:
        response = Objects.GetUserOwnedObject(accesstoken, "applications", appid, params, useragent)
    else:
        print("Must supply an id for an entra object.")

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))


# o365
@exchange_app.command("message")
def exchange_message(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    userid: Annotated[str, typer.Option(help="User upn.")],
    extractattachments: Annotated[bool, typer.Option(help="Extract attachments from messages into the loot folder.")] = False,
    lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted blob.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/Exchange/",
    format: Annotated[str, typer.Option(help="Message body format to return (text or html).")] = "text",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (&$search=Keyword&$top=10")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if format != "text" and format != "html":
        format = "text"
    
    if userid == None:
        tokendata = Authentication.Token.Decode(accesstoken)

        if "unique_name" in tokendata:
            userid = tokendata["unique_name"]
        elif "upn" in tokendata:
            userid = tokendata["upn"]
        else: 
            userid = tokendata["oid"]

    response = Exchange.GetExchangeMessages(accesstoken, userid, extractattachments, lootpath, format, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@onedrive_app.command("item")
def onedrive_item(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    # id: Annotated[str, typer.Option(help="Id of user, site or group (oid or upn) to get the documents from.")] = None,
    # type: Annotated[str, typer.Option(help="Id of user, site or group (oid or upn) to get the documents from.")] = "user",
    extractdriveitems: Annotated[bool, typer.Option(help="Extract documents into the loot folder.")] = False,
    lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted blob.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/OneDrive/",
    # params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (&$search=Keyword&$top=10")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    drive = OneDrive.GetDrive(accesstoken, useragent)

    if drive.status_code == 200:
        drive = json.loads(drive.content.decode("utf-8"))

        if isinstance(drive, dict):
            sharedItems = OneDrive.GetSharedWithMe(accesstoken, useragent)

            if sharedItems.status_code == 200:
                sharedItems = json.loads(sharedItems.content.decode("utf-8"))

                if isinstance(sharedItems, dict):
                    if len(sharedItems["value"]) > 0:
                        drive.update({"sharedItems": sharedItems["value"]})
                    else:
                        drive.update({"sharedItems": None})

            items = OneDrive.GetDriveItems(accesstoken, drive, useragent)
            if items.status_code == 200:
                items = json.loads(items.content.decode("utf-8"))

                if isinstance(items, dict):
                    if len(items["value"]) > 0:
                        drive.update({"driveItems": items["value"]})
                    else:
                        drive.update({"driveItems": None})

            
            # Download documents
            if extractdriveitems:
                OneDrive.ExtractDriveItems(accesstoken, drive, lootpath, useragent)

            if rich:
                pass
            else:
                print(drive)
    else:
        print("No drive items found!")

@teams_app.command("message")
def teams_message(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    # extractmessages: Annotated[bool, typer.Option(help="Extract attachments from messages into the loot folder.")] = False,
    # lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted blob.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/Teams",
    # params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (&$search=Keyword&$top=10")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = Teams.GetMessages(accesstoken, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@substrate_app.command("teams-user")
def substrate_get_teams_users(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    keyword: Annotated[str, typer.Option(help="Substring to search for.")] = "",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    response = Substrate.SearchTeamUsers(accesstoken, keyword, useragent)

    if rich:
        pass
    else:
        print(response)

@substrate_app.command("teams-message")
def substrate_get_teams_messages(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    userid: Annotated[str, typer.Option(help="User upn.")] = None,
    keyword: Annotated[str, typer.Option(help="Substring to search for in messages.")] = "password",
    size: Annotated[int, typer.Option(help="Number of results to return.")] = 50,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if userid == None:
        tokenInfo = Authentication.Token.Decode(accesstoken)

        if "unique_name" in tokenInfo:
            userid = tokenInfo["unique_name"]
        elif "upn" in tokenInfo:
            userid = tokenInfo["upn"]

    response = Substrate.SearchTeamMessages(accesstoken, userid, size, keyword, useragent)

    if rich:
        pass
    else:
        print(response)

# Azure Resource Management
@get_app.command("subscription")
def subscriptions_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Subscriptions api version (https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/list?view=rest-resources-2022-12-01&tabs=HTTP).")] = "2022-12-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($select=id,displayName) - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = Subscriptions.GetSubscriptions(accesstoken, params, useragent, apiversion)

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))

@get_app.command("resource")
def resources_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Resource api version (https://learn.microsoft.com/en-us/rest/api/resources/resources/list?view=rest-resources-2021-04-01).")] = "2022-12-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($select=id,displayName) - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    subscriptions = Subscriptions.GetSubscriptions(accesstoken, None, useragent)
    subscriptions = json.loads(subscriptions.content.decode("utf-8"))["value"]
    response = Resources.GetResources(accesstoken, subscriptions, params, useragent, apiversion)

    if rich:
        pass
    else:
        print(response)

@get_app.command("rbacrole")
def rbacrole_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Azure RBAC api version (https://learn.microsoft.com/en-us/rest/api/authorization/versions).")] = "2022-04-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=principalId eq 'xxxx-xxxx-xxxx-xxx-xxxx') - https://learn.microsoft.com/bs-latn-ba/azure/role-based-access-control/role-assignments-list-rest#list-role-assignments")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):

    response = None

    subscriptions = Subscriptions.GetSubscriptions(accesstoken, None, useragent)
    subscriptions = json.loads(subscriptions.content.decode("utf-8"))["value"]
    
    if len(subscriptions) > 0:
        response = RBACRoles.GetRoleAssignments(accesstoken, subscriptions, params, useragent, apiversion)

        if isinstance(response, list):
            if rich:
                pass
            else:
                print(response)
        else:
            print(response)

@brute_app.command("storage")
def storage_brute(
    storageaccount: Annotated[str, typer.Option(help="Name of storage accounts to brute comma-separated. (-->storageaccount<--.blob.core.windows.net)")],
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    sastoken: Annotated[str, typer.Option(help="SAS token to use in the requests (without beginning ?).")] = None,
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services & https://learn.microsoft.com/en-us/rest/api/storageservices/previous-azure-storage-service-versions).")] = "2024-11-04",
    wordlist: Annotated[typer.FileText, typer.Option(help="Path to wordlist to use.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Modules/ARM/Wordlists/container-names.txt",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (include=deleted,versions - https://learn.microsoft.com/en-us/rest/api/storageservices/blob-service-rest-api.")] = None,
    listblobs: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = Storage.BruteContainers(accesstoken, storageaccount, sastoken, wordlist, params, listblobs, useragent, apiversion)

    if isinstance(response, list):
        for container in response:
            print(container)
    else:
        print(response)

@storage_app.command("container")
def storage_container(
    storageaccount: Annotated[str, typer.Option(help="Name of the storage account (-->storageaccount<--.blob.core.windows.net)")],
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    sastoken: Annotated[str, typer.Option(help="SAS token to use in the requests (without beginning ?).")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (include=metadata,deleted,system - https://learn.microsoft.com/en-us/rest/api/storageservices/list-containers2?tabs=microsoft-entra-id.")] = None,
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services & https://learn.microsoft.com/en-us/rest/api/storageservices/previous-azure-storage-service-versions).")] = "2024-11-04",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = Storage.GetContainer(accesstoken, storageaccount, sastoken, params, useragent, apiversion)

    if isinstance(response, dict):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response.text)

@storage_app.command("blob")
def storage_blob(
    storageaccount: Annotated[str, typer.Option(help="Name of the storage account (-->storageaccount<--.blob.core.windows.net)")],
    container: Annotated[str, typer.Option(help="Name of blob container.")],
    blob: Annotated[str, typer.Option(help="Name of the blob to get.")] = None,
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    sastoken: Annotated[str, typer.Option(help="SAS token to use in the requests (without beginning ?).")] = None,
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services & https://learn.microsoft.com/en-us/rest/api/storageservices/previous-azure-storage-service-versions).")] = "2024-11-04",
    lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted blob.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/Storage/",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (versionId=2024-03-29T20:55:40.8265593Z - https://learn.microsoft.com/en-us/rest/api/storageservices/blob-service-rest-api.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = Storage.GetBlob(accesstoken, storageaccount, container, blob, sastoken, lootpath, params, useragent, apiversion)

    if isinstance(response, dict):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@get_app.command("webapp")
def webapp_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Storage api version to use ().")] = "2023-12-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=resourceType eq 'Microsoft.KeyVault/vaults' - https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/get?view=rest-appservice-2023-12-01&tabs=HTTP")] = "$filter=resourceType eq 'Microsoft.Web/sites'",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    response = Subscriptions.GetSubscriptions(accesstoken, None, useragent)

    if response.status_code == 200:
        subscriptions = json.loads(response.content.decode("utf-8"))["value"]
        response = Resources.GetResources(accesstoken, subscriptions, params, useragent)
        
        if isinstance(response, list):
            sites = response
            sites = WebApp.GetSite(sites, accesstoken, useragent, apiversion)

            if isinstance(sites, list):
                if rich:
                    pass
                else:
                    print(sites)
        else:
            print(response)
    else:
        print(response)

@get_app.command("functionapp")
def functionapp_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/list-functions?view=rest-appservice-2023-12-01).")] = "2023-12-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=resourceType eq 'Microsoft.KeyVault/vaults' - https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/get?view=rest-appservice-2023-12-01&tabs=HTTP")] = "$filter=resourceType eq 'Microsoft.Web/sites'",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    response = Subscriptions.GetSubscriptions(accesstoken, None, useragent)

    if response.status_code == 200:
        subscriptions = json.loads(response.content.decode("utf-8"))["value"]
        response = Resources.GetResources(accesstoken, subscriptions, params, useragent)
        
        if isinstance(response, list):
            functionapps = []
            
            for functionapp in response:
                if functionapp["kind"] == "functionapp":
                    functionapps.append(functionapp)

            functionapps = FunctionApp.GetFunction(functionapps, accesstoken, useragent, apiversion)

            if isinstance(functionapps, list):
                if rich:
                    pass
                else:
                    print(functionapps)
        else:
            print(response)
    else:
        print(response)

@get_app.command("keyvault")
def keyvault_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    keyvaultaccesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services & https://learn.microsoft.com/en-us/rest/api/storageservices/previous-azure-storage-service-versions).")] = "2022-07-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=resourceType eq 'Microsoft.KeyVault/vaults' - https://learn.microsoft.com/en-us/rest/api/keyvault/keyvault/vaults/list?view=rest-keyvault-keyvault-2022-07-01&tabs=HTTP")] = "$filter=resourceType eq 'Microsoft.KeyVault/vaults'",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    response = Subscriptions.GetSubscriptions(accesstoken, None, useragent)

    if response.status_code == 200:
        subscriptions = json.loads(response.content.decode("utf-8"))["value"]
        response = Resources.GetResources(accesstoken, subscriptions, params, useragent)

        if isinstance(response, list):
            vaults = response
            vaults = KeyVault.GetKeyVaultURI(vaults, accesstoken, apiversion, useragent)

            if isinstance(vaults, list):
                vaults = KeyVault.GetKeyVaultSecret(vaults, keyvaultaccesstoken, useragent)
                
                if rich:
                    pass
                else:
                    print(vaults)
        else:
            print(response)
    else:
        print(response)

@get_app.command("vm")
def vm_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/compute/virtual-machines/get?view=rest-compute-2024-07-01.")] = "2024-07-01",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=resourceType eq 'Microsoft.Compute/virtualMachines' - https://learn.microsoft.com/en-us/rest/api/compute/virtual-machines/get?view=rest-compute-2024-07-01.")] = "$filter=resourceType eq 'Microsoft.Compute/virtualMachines'",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    response = Subscriptions.GetSubscriptions(accesstoken, None, useragent)

    if response.status_code == 200:
        subscriptions = json.loads(response.content.decode("utf-8"))["value"]
        response = Resources.GetResources(accesstoken, subscriptions, params, useragent)
        # publicIPs = Resources.GetResources(accesstoken, subscriptions, "$filter=resourceType eq 'Microsoft.Network/publicIPAddresses'", useragent)
        

        if isinstance(response, list):
            vms = response
            vms = VM.GetVM(vms, accesstoken, apiversion, useragent)

            if isinstance(vms, list):
                
                if rich:
                    pass
                else:
                    print(vms)
        else:
            print(response)
    else:
        print(response)

@cmd_app.command("kuduapi")
def kuduapi_cmd(
    kuduuri: Annotated[str, typer.Option(help="Full url to the SCM/kudu instance running the app (https://<appname>.scm.azurewebsites.net or https://<appname>.p.azurewebsites.net)")],
    user: Annotated[str, typer.Option(help="Kudu username.")],
    password: Annotated[str, typer.Option(help="Kudu password.")],
    cmd: Annotated[str, typer.Option(help="Command.")] = "ls -alh",
    dir: Annotated[str, typer.Option(help="Working directory.")] = "/home/site/wwwroot/",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    #https://learn.microsoft.com/sr-cyrl-rs/azure/app-service/resources-kudu
    #https://learn.microsoft.com/en-us/visualstudio/deployment/tutorial-import-publish-settings-azure?view=vs-2022
    #https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-services/az-azure-app-service#obtain-credentials-and-get-access-to-the-webapp-code
    #https://github.com/projectkudu/kudu/wiki/REST-API#zip-deployment
    #https://www.mobzystems.com/blog/kudu-from-powershell/

    response = None
    
    response = KuduAPI.KuduCommand(kuduuri, user, password, cmd, dir, useragent)

    if response.status_code == 200:
        response = json.loads(response.content.decode("utf-8"))

        if isinstance(response, dict):
            if response["ExitCode"] != 1:
                if rich: 
                    pass
                else:
                    print(response["Output"])
    else:
        print(response)

@update_app.command("kuduapi")
def kuduapi_upload(
    kuduuri: Annotated[str, typer.Option(help="Full url to the SCM/kudu instance running the app (https://<appname>.scm.azurewebsites.net or https://<appname>.p.azurewebsites.net)")],
    user: Annotated[str, typer.Option(help="Kudu username.")],
    password: Annotated[str, typer.Option(help="Kudu password.")],
    file: Annotated[typer.FileBinaryRead, typer.Option(help="Local file to upload.")],
    dir: Annotated[str, typer.Option(help="Kudu password.")] = "/site/wwwroot/",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    #https://learn.microsoft.com/sr-cyrl-rs/azure/app-service/resources-kudu
    #https://learn.microsoft.com/en-us/visualstudio/deployment/tutorial-import-publish-settings-azure?view=vs-2022
    #https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-services/az-azure-app-service#obtain-credentials-and-get-access-to-the-webapp-code
    #https://github.com/projectkudu/kudu/wiki/REST-API#zip-deployment
    #https://www.mobzystems.com/blog/kudu-from-powershell/

    response = None
    
    response = KuduAPI.KuduUpload(kuduuri, user, password, file, dir, useragent)

    if isinstance(response, dict):
        if rich: 
            pass
        else:
            print(response)
    else:
        print(response)

@get_app.command("kuduapi")
def kuduapi_download(
    kuduuri: Annotated[str, typer.Option(help="Full url to the SCM/kudu instance running the app (https://<appname>.scm.azurewebsites.net or https://<appname>.p.azurewebsites.net)")],
    user: Annotated[str, typer.Option(help="Kudu username.")],
    password: Annotated[str, typer.Option(help="Kudu password.")],
    file: Annotated[str, typer.Option(help="Path of file including name to download. Note that all paths are automatically prefixed with /home.")],
    # dir: Annotated[str, typer.Option(help="Kudu password.")] = "/home/site/wwwroot/",
    lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted files from kudu.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/Kudu/",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    #https://learn.microsoft.com/sr-cyrl-rs/azure/app-service/resources-kudu
    #https://learn.microsoft.com/en-us/visualstudio/deployment/tutorial-import-publish-settings-azure?view=vs-2022
    #https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-services/az-azure-app-service#obtain-credentials-and-get-access-to-the-webapp-code
    #https://github.com/projectkudu/kudu/wiki/REST-API#zip-deployment
    #https://www.mobzystems.com/blog/kudu-from-powershell/

    response = None
    
    response = KuduAPI.KuduDownload(kuduuri, user, password, file, lootpath, useragent)

    if isinstance(response, dict):
        if rich: 
            pass
        else:
            print(response)
    else:
        print(response)

@connect_app.command("sql")
def sql_connect(
    connectionstring: Annotated[str, typer.Option(help="A connection string that will be parsed.")] = None,
    servername: Annotated[str, typer.Option(help="Server name (full FQDN) - <servername>.database.windows.net:<optional port number>")] = None,
    database: Annotated[str, typer.Option(help="Name of the database in the server that you want to interact with.")] = None,
    user: Annotated[str, typer.Option(help="DB username.")] = None,
    password: Annotated[str, typer.Option(help="DB user password.")] = None,
    query: Annotated[str, typer.Option(help="Oneshot SQL query to execute.")] = None,
    dumpall: Annotated[bool, typer.Option(help="Dump all databases in the server.")] = False,
    interactive: Annotated[bool, typer.Option(help="Start interactive shell with the server.")] = False,
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1"
):
    response = None
    
    response = SQL.main(connectionstring, servername, database, user, password, query, dumpall, interactive, accesstoken, useragent)

    if isinstance(response, str):
        print(response)


# Other services

@query_app.command("security")
def security_query(
    user: Annotated[str, typer.Option(help="Username (use upn format if not providing tenant id/alias).")] = None,
    password: Annotated[str, typer.Option(help="Password for user or client secret.")] = None,
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    sccauthtoken: Annotated[str, typer.Option(help="Sccauth token from cookies when logged into security.microsoft.com portal.")] = None,
    xsrftoken: Annotated[str, typer.Option(help="X-Xsrf-token from headers when logged into security.microsoft.com portal.")] = None,
    query: Annotated[str, typer.Option(help="KQL query. Use the default query to enumerate resources or come up with your own.")] = """
ExposureGraphEdges
| where SourceNodeLabel has_any ("user", "group", "role", "service", "managed") and TargetNodeLabel startswith "microsoft"
| mv-expand EdgeProperties
| extend data = EdgeProperties.rawData
| extend permissions = data.permissions
| extend roles = permissions.roles
| mv-expand roles
| extend roleName = roles.name
| project SourceNodeLabel, SourceNodeName, roleName, TargetNodeLabel, TargetNodeName
| order by SourceNodeName asc
""",
    start: Annotated[str, typer.Option(help="Start zulu time (YYYY-mm-ddTHH:MM:sssZ).")] = None,
    end: Annotated[str, typer.Option(help="End zulu time (YYYY-mm-ddTHH:MM:sssZ).")] = None,
    maxrecords: Annotated[int, typer.Option(help="Number of records to return")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if accesstoken == None:
        response = ThreatHunting.SeleniumRunQuery(user, password, sccauthtoken, xsrftoken, query, start, end, maxrecords, useragent)
    else:
        response = ThreatHunting.MTPRunQuery(accesstoken, query, start, end, maxrecords, useragent)

    print()

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@connect_app.command("liveresponse")
def security_liveresponse(
    machineid: Annotated[str, typer.Option(help="This can be the id of the machine in MDE or can be the FQDN or partial name of the host.")],
    user: Annotated[str, typer.Option(help="Username (use upn format if not providing tenant id/alias).")] = None,
    password: Annotated[str, typer.Option(help="Password for user or client secret.")] = None,
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    sccauthtoken: Annotated[str, typer.Option(help="Sccauth token from cookies when logged into security.microsoft.com portal.")] = None,
    xsrftoken: Annotated[str, typer.Option(help="X-Xsrf-token from headers when logged into security.microsoft.com portal.")] = None,
    lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted blob.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/LiveResponse/",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if accesstoken == None:
        response = LiveResponse.SeleniumLiveResponse(user, password, sccauthtoken, xsrftoken, machineid, lootpath, useragent)
    else:
        response = LiveResponse.MTPLiveResponse(accesstoken, machineid, lootpath, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@intune_app.command("device")
def intune_device(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=deviceName eq 'hostname')")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    
    response = Intune.GetManagedDevice(accesstoken, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@intune_app.command("cloudpc")
def intune_device(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=deviceName eq 'hostname')")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    
    response = Intune.GetCloudPC(accesstoken, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@intune_app.command("localcredential")
def intune_local_credentials(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    clientname: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu",
    clientversion: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "0.0.1",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=deviceId eq 'xxxx-xxx-xxx-xxxx')")] = None,
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    
    response = Intune.GetDeviceLocalCredentials(accesstoken, clientname, clientversion, params, useragent)

    if isinstance(response, dict):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@intune_app.command("bitlockerkey")
def intune_bitlocker_key(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request ($filter=deviceId eq 'xxxx-xxx-xxx-xxxx')")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    
    response = Intune.GetDeviceBitLockerKey(accesstoken, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@intune_app.command("managementscript")
def intune_management_script(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    format: Annotated[str, typer.Option(help="The format of the script content. Options are b64 or text")] = "b64",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    
    response = Intune.GetDeviceManagementScript(accesstoken, format, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)

@intune_app.command("shellscript")
def intune_management_script(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    format: Annotated[str, typer.Option(help="The format of the script content. Options are b64 or text")] = "b64",
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request. ")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None
    
    response = Intune.GetDeviceShellScript(accesstoken, format, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)


if __name__ == "__main__":
    app()