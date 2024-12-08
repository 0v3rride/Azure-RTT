import enum

# https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth-ropc
class GrantType(str, enum.Enum):
    ropc = "ropc"
    clientsecret = "clientsecret"
    devicecode = "devicecode"
    authcode = "authcode"
    certificate = "certificate"
    implicit = "implicit"
    interactive = "interactive"