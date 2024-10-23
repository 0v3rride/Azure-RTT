import typer
from typing_extensions import Annotated
from rich import print
from rich.console import Console
from rich.table import Table
import os
import json
import azure.identity

from Modules.Settings import GrantType
from Modules.Credential import Spray
import Modules.Settings.Clients
import Modules.Settings.Scopes
import Tokens.Token
import Modules.Settings
from Modules.Entra import Users, Roles, AdministrativeUnits, Groups, Policies, Apps, ServicePrincipals, Objects
from Modules.O365 import Teams, Exchange, OneDrive, OneNote, SharePoint
from Modules.ARM import Storage, SQL, KeyVault, Resources, Subscriptions, RBACRoles, KuduAPI, VM, PublicIPAddress
from Modules.Security import ThreatHunting
from Modules.ARM.AppService import WebApp, FunctionApp
from Modules.Enumeration import Tenant


root_dir = os.path.dirname(os.path.abspath(__file__))
error_console = Console(stderr=True)

app = typer.Typer()
tenant_app = typer.Typer()
token_app = typer.Typer()
spray_app = typer.Typer()
tenant_app = typer.Typer()
entrauser_app = typer.Typer()
entragroup_app = typer.Typer()
entrarole_app = typer.Typer()
entraadministrativeunit_app = typer.Typer()
entraapp_app = typer.Typer()
entraserviceprincipal_app = typer.Typer()
entraobject_app = typer.Typer()
intune_app = typer.Typer()
roleassignment_app = typer.Typer()
functionapp_app = typer.Typer()
webapp_app = typer.Typer()
kuduapi_app = typer.Typer()
keyvault_app = typer.Typer()
subscriptions_app = typer.Typer()
resources_app = typer.Typer()
sql_app = typer.Typer()
storage_app = typer.Typer()
vm_app = typer.Typer()
security_app = typer.Typer()
onenote_app = typer.Typer()
onedrive_app = typer.Typer()
teams_app = typer.Typer()
sharepoint_app = typer.Typer()
exchange_app = typer.Typer()


#app.add_typer(spray_app, name="spray", help="Spray credentials and check for MFA gaps in services.")
app.add_typer(token_app, name="token", help="Use an OAuth grant to get tokens")
app.add_typer(entrauser_app, name="entrauser", help="Entra user related commands (get, update).")
app.add_typer(entragroup_app, name="entragroup", help="Entra user related commands (get, update).")
app.add_typer(entrarole_app, name="entrarole")
app.add_typer(entraadministrativeunit_app, name="entraadministrativeunit")
app.add_typer(entraapp_app, name="entraapp")
app.add_typer(entraserviceprincipal_app, name="entraserviceprincipal")
app.add_typer(entraobject_app, name="entraobject")
app.add_typer(intune_app, name="intune")
app.add_typer(keyvault_app, name="keyvault")
app.add_typer(functionapp_app, name="functionapp")
app.add_typer(webapp_app, name="webapp")
app.add_typer(kuduapi_app, name="kuduapi", help="Use credentials from publishing profiles of Azure App Service apps, etc. to interact with the apps accompanying kudu/scm managment api.")
app.add_typer(resources_app, name="resource")
app.add_typer(subscriptions_app, name="subscription")
app.add_typer(roleassignment_app, name="roleassignment")
app.add_typer(sql_app, name="sql")
app.add_typer(storage_app, name="storage")
app.add_typer(vm_app, name="vm")
app.add_typer(security_app, name="security")
app.add_typer(onenote_app, name="onenote")
app.add_typer(onedrive_app, name="onedrive")
app.add_typer(teams_app, name="teams")
app.add_typer(sharepoint_app, name="sharepoint")
app.add_typer(exchange_app, name="exchange")
app.add_typer(tenant_app, name="tenant", help="Enumerate tenant information from public Azure rest api endpoints.")



@tenant_app.command("getregistereddomains")
def tenant_getregistereddomains(
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
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")] = None,
    client: Annotated[str, typer.Option(help="The client id of the app to use to authenticate against.")] = "office",
    scope: Annotated[str, typer.Option(help="Resources/scopes to request the token for.")] = "graph",
    # granttype: Annotated[GrantType.GrantType, typer.Option(help="OAuth flow to use to get token.")] = GrantType.GrantType.ropc,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    mfacheck: Annotated[bool, typer.Option(help="Check which services have MFA enabled if a valid set of credentials are found.")] = False,
    savetokens: Annotated[bool, typer.Option(help="Save token data to ../Loot/Tokens/tokencache.json.")] = False,
    # rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    Spray.main(userlist, passwordlist, tenant, client, scope, useragent, mfacheck, savetokens)

# FIXME Add oauth2/token (v1) endpoint to workaround issues with newer v2 not returning a refresh token
@token_app.command("get", help="Acquire tokens via specified OAuth grant.")
def token_get(
    user: Annotated[str, typer.Option(help="Username (use upn format if not providing tenant id/alias).")] = None,
    password: Annotated[str, typer.Option(help="Password for user or client secret.")] = None,
    certificate: Annotated[typer.FileBinaryRead, typer.Option(help="File path to .pfx.")] = None,
    tenant: Annotated[str, typer.Option(help="Tenant id or alias if upn format was not used for user argument.")] = None,
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
            response = Tokens.Token.ResourceOwnerPasswordCredentials(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "clientsecret":
            response = Tokens.Token.ClientSecretCredentials(password, tenant, client, scope, usecae, endpointversion, useragent)
        case "devicecode":
            response = Tokens.Token.DeviceCode(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "authcode":
            response = Tokens.Token.AuthorizationCode(user, password, tenant, client, scope, usecae, endpointversion, useragent)
        case "certificate":
            response = Tokens.Token.CertificateBasedAuthentication(certificate, password, tenant, client, scope, usecae, endpointversion, useragent)
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
            else:
                print(json.loads(response.content.decode("utf-8")))
        except:
            pass

@token_app.command("refresh", help="Refresh an access token or acquire a new token for a different scope/service.")
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
    response = Tokens.Token.Refresh(refreshtoken, tenant, client, scope, usecae, endpointversion, useragent)

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))

@token_app.command("decode", help="Decode jwt access token to view token properties.")
def token_decode(
    accesstoken: Annotated[str, typer.Option(help="Refresh token.")]
):
    print(Tokens.Token.Decode(accesstoken))
    
@token_app.command("list", help="List tokens in tokencache.json.")
def token_list(
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if isinstance(response, dict):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)


@entrauser_app.command("get", help="Get a user or all users and their specified properties. Can get customsecurityattributes.")
def entrauser_get(
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

#FIXME: finish this later
@entrauser_app.command("update", help="Update a user's properties including their password (https://learn.microsoft.com/en-us/graph/api/user-update?view=graph-rest-1.0&tabs=http#request-2).")
def entrauser_update(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    id: Annotated[str, typer.Option(help="User object id or upn.")],
    # help="Parameters to send in the body of the request (passwordProfile=n3WSuP3rS3cureP@$$w0rd)."
    params: Annotated[str, typer.Option(help="JSON string body to send in the request ('{\"passwordProfile\": {\"password\":\"n3WSuP3rS3cur3P@$$w0rd!\", \"forceChangePasswordNextSignIn\": \"false\"}}).")],
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1"
):
    response = None

    response = Users.UpdateUser(accesstoken, id, params, useragent)
    
    print(response)
    typer.echo("updated user")


@entraadministrativeunit_app.command("get", help="Acquire all administrative units or a specified unit along with their scoped members, members and entra role it is scoped to.")
def entraadministrativeunit_get(
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


@entrarole_app.command("get", help="Acquire all entra roles or a specific role and it's members.")
def entrarole_get(
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


@entragroup_app.command("get", help="Acquire all entra groups or a specific group and it's members.")
def entragroup_get(
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


@entraapp_app.command("get", help="Get an app or all apps and their specified properties.")
def entraapp_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    id: Annotated[str, typer.Option(help="Application id.")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (i.e. $select=id,displayname&$top=10) - https://learn.microsoft.com/en-us/graph/query-parameters?tabs=http.")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    if id:
        response = Apps.GetApplication(accesstoken, id, params, useragent)
    else:
        response = Apps.GetAllApplications(accesstoken, params, useragent)

    if rich:
        pass
    else:
        print(json.loads(response.content.decode("utf-8")))


@entraserviceprincipal_app.command("get", help="Get a service principal or all service principals and their specified properties.")
def entraserviceprincipal_get(
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


@entraobject_app.command("getbyowner", help="Get objects owned by a user, service principal or an application (choose one).")
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



@exchange_app.command("get", help="Retrieve exchange messages using current context.")
def exchange_get(
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

    response = Exchange.GetExchangeMessages(accesstoken, userid, extractattachments, lootpath, format, params, useragent)

    if isinstance(response, list):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response)


@onedrive_app.command("get", help="Retrieve onedrive items and shared items using current context.")
def onedrive_get(
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


@teams_app.command("get", help="Retrieve teams messages using current context.")
def teams_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    extractmessages: Annotated[bool, typer.Option(help="Extract attachments from messages into the loot folder.")] = False,
    lootpath: Annotated[str, typer.Option(help="Set path for loot folder which will contain the extracted blob.")] = f"{os.path.dirname(os.path.abspath(__file__))}/Loot/Teams",
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




@subscriptions_app.command("get", help="Get subscriptions associated with current token.")
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


@resources_app.command("get", help="Get resources associated with current token.")
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


@roleassignment_app.command("get", help="Get ARM RBAC role assignments associated with current token.")
def roleassignment_get(
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


@storage_app.command("brute", help="Brute container names for a storage account")
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


@storage_app.command("getcontainer", help="List containers in storage account under current context")
def storage_get_container(
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


@storage_app.command("listblob", help="List blobs in a specified storage account and container.")
def storage_list_blob(
    storageaccount: Annotated[str, typer.Option(help="Name of the storage account (-->storageaccount<--.blob.core.windows.net)")],
    container: Annotated[str, typer.Option(help="Name of blob container.")],
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")] = None,
    sastoken: Annotated[str, typer.Option(help="SAS token to use in the requests (without beginning ?).")] = None,
    params: Annotated[str, typer.Option(help="Odata query parameters to send in the request (include=versions,deleted,uncommittedblobs&maxresults=10 - https://learn.microsoft.com/en-us/rest/api/storageservices/list-blobs?tabs=microsoft-entra-id.")] = "include=versions,deleted,uncommittedblobs,metadata,copy,snapshots",
    apiversion: Annotated[str, typer.Option(help="Storage api version to use (https://learn.microsoft.com/en-us/rest/api/storageservices/versioning-for-the-azure-storage-services & https://learn.microsoft.com/en-us/rest/api/storageservices/previous-azure-storage-service-versions).")] = "2024-11-04",
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = Storage.ListBlob(accesstoken, storageaccount, container, sastoken, params, useragent, apiversion)

    if isinstance(response, dict):
        if rich:
            pass
        else:
            print(response)
    else:
        print(response.text)


@storage_app.command("getblob", help="Retrieve a blob from a blob storage account container. Blob is extracted to the path specified by the lootpath option.")
def storage_get_blob(
    storageaccount: Annotated[str, typer.Option(help="Name of the storage account (-->storageaccount<--.blob.core.windows.net)")],
    container: Annotated[str, typer.Option(help="Name of blob container.")],
    blob: Annotated[str, typer.Option(help="Name of the blob to get.")],
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


@webapp_app.command("get", help="Retrieve web apps under current context which includes publish profile/deploy credentials.")
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


@functionapp_app.command("get", help="Retrieve function apps under current context which includes publish profile/deploy credentials.")
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


@keyvault_app.command("get", help="Retrieve accessible key vaults and all information under current context.")
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



@vm_app.command("get", help="Retrieve accessible vms under current context.")
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


@security_app.command("query", help="Run defender 365 advanced threat hunting query.")
def vm_get(
    accesstoken: Annotated[str, typer.Option(help="Access token to use to make the request.")],
    query: Annotated[str, typer.Option(help="KQL query. Use the default query to enumerate resources or come up with your own.")] = """
ExposureGraphEdges
| where SourceNodeLabel has_any ("user", "group", "role", "service", "managed") and TargetNodeLabel matches regex "microsoft\\.*"
| mv-expand EdgeProperties
| extend data = EdgeProperties.rawData
| extend permissions = data.permissions
| extend roles = permissions.roles
| mv-expand roles
| extend roleName = roles.name
| project SourceNodeLabel, SourceNodeName, roleName, TargetNodeLabel, TargetNodeName
| order by SourceNodeName asc
""",
    timespan: Annotated[str, typer.Option(help="Timespan ISO 8601 format")] = None,
    useragent: Annotated[str, typer.Option(help="User agent string value to use with request.")] = "habu/0.0.1",
    rich: Annotated[bool, typer.Option(help="Output results in rich format, otherwise output as raw json.")] = False
):
    response = None

    response = ThreatHunting.RunQuery(accesstoken, query, timespan, useragent)

    



#FIXME: include <name>.mysql.database.azure.com
@sql_app.command("connect", help="Connect to an AZ SQL server - <servername>.database.windows.net.")
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

@kuduapi_app.command("command", help="Interact with the /api/command rest api point of the specified kudu instance.")
def kuduapi_command(
    kuduuri: Annotated[str, typer.Option(help="Full url to the SCM/kudu instance running the app (https://<appname>.scm.azurewebsites.net or https://<appname>.p.azurewebsites.net)")],
    user: Annotated[str, typer.Option(help="Kudu username.")],
    password: Annotated[str, typer.Option(help="Kudu password.")],
    cmd: Annotated[str, typer.Option(help="Kudu password.")] = "ls -alh",
    dir: Annotated[str, typer.Option(help="Kudu password.")] = "/home/site/wwwroot/",
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

#FIXME Get uploading working
@kuduapi_app.command("upload", help="Upload a file to the specified path on the kudu instance.")
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


@kuduapi_app.command("download", help="Specify a file to download from the kudu instance.")
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



if __name__ == "__main__":
    app()
