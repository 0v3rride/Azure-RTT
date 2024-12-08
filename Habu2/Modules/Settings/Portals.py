import enum

# https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth-ropc
class Portal(str, enum.Enum):
    security = "security"
    intune = "intune"
    azure = "azure"