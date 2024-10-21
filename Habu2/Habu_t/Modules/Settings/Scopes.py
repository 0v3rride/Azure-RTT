# scopes v2.0/resources v1.0 - https://learn.microsoft.com/en-us/entra/identity-platform/scopes-oidc
# https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide
# https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/managed-identities-status#azure-services-that-support-azure-ad-authentication

Scope = {
    "graph": "https://graph.microsoft.com//.default openid profile offline_access", # AADGraph API https://graph.windows.net - https://stackoverflow.com/questions/62513980/whats-the-difference-between-graph-windows-net-and-graph-microsoft-com
    "management": "https://management.azure.com//.default openid profile offline_access", # or https://management.core.windows.net//.default
    "o365": "https://outlook.office365.com//.default openid profile offline_access", # or https://outlook.office.com Try different user agents with this when using requests (yes)
    "teamsv1": "https://api.spaces.skype.com//.default openid profile offline_access",
    "teams": "https://teams.microsoft.com//.default openid profile offline_access",
    "security center": "https://security.microsoft.com//.default openid profile offline_access",
    "compliance": "https://compliance.microsoft.com//.default openid profile offline_access",
    "database": "https://database.windows.net//.default openid profile offline_access",
    "storage": "https://storage.azure.com//.default openid profile offline_access",
    "key vault": "https://vault.azure.net//.default openid profile offline_access", #vaultcore.azure.net?
    "device management": "https://devicemanagement.microsoft.com//.default openid profile offline_access", #intune?
    "cosmos": "https://cosmos.azure.com//.default openid profile offline_access",
    "monitor": "https://monitor.azure.com//.default openid profile offline_access",
    "digital twins": "https://digitaltwins.azure.net//.default openid profile offline_access",
    "datalake": "https://datalake.azure.net//.default openid profile offline_access", 
    "synapse": "https://dev.azuresynapse.net//.default openid profile offline_access", 
    "api management": "https://management.azure-api.net//.default openid profile offline_access", 
    "signalr": "https://signalr.azure.com/.default openid profile offline_access",
    "eventgrid": "https://eventgrid.azure.net//.default openid profile offline_access",
    "iothub": "https://iothubs.azure.com/.default openid profile offline_access",
    "ml": "https://ml.azure.com//.default openid profile offline_access",
    # "Office": "https://www.office.com",
}

def GetScope(name):
    try:
        return Scope.get(name, name)
    except KeyError as ke:
        return name




#https://github.com/absolomb/FindMeAccess/blob/main/findmeaccess.py
#https://learn.microsoft.com/en-us/azure/security/fundamentals/azure-domains

# https://*.redis.cache.windows.net/
# "Environment": {
#         "Name": "AzureCloud",
#         "Type": "Built-in",
#         "OnPremise": false,
#         "ServiceManagementUrl": "https://management.core.windows.net/",
#         "ResourceManagerUrl": "https://management.azure.com/",
#         "ManagementPortalUrl": "https://portal.azure.com",
#         "PublishSettingsFileUrl": "https://go.microsoft.com/fwlink/?LinkID=301775",
#         "ActiveDirectoryAuthority": "https://login.microsoftonline.com",
#         "GalleryUrl": "https://gallery.azure.com/",
#         "GraphUrl": "https://graph.windows.net/",
#         "ActiveDirectoryServiceEndpointResourceId": "https://management.core.windows.net/",
#         "StorageEndpointSuffix": "core.windows.net",
#         "SqlDatabaseDnsSuffix": ".database.windows.net",
#         "TrafficManagerDnsSuffix": "trafficmanager.net",
#         "AzureKeyVaultDnsSuffix": "vault.azure.net",
#         "AzureKeyVaultServiceEndpointResourceId": "https://vault.azure.net",
#         "GraphEndpointResourceId": "https://graph.windows.net/",
#         "DataLakeEndpointResourceId": "https://datalake.azure.net/",
#         "BatchEndpointResourceId": "https://batch.core.windows.net/",
#         "AzureDataLakeAnalyticsCatalogAndJobEndpointSuffix": "azuredatalakeanalytics.net",
#         "AzureDataLakeStoreFileSystemEndpointSuffix": "azuredatalakestore.net",
#         "AdTenant": "common",
#         "ContainerRegistryEndpointSuffix": "azurecr.io",
#         "VersionProfiles": [],
#         "ExtendedProperties": {
#           "ManagedHsmServiceEndpointSuffix": "managedhsm.azure.net",
#           "AzureAttestationServiceEndpointSuffix": "attest.azure.net",
#           "MicrosoftGraphEndpointResourceId": "https://graph.microsoft.com/",
#           "ContainerRegistryEndpointResourceId": "https://management.azure.com",
#           "MicrosoftGraphUrl": "https://graph.microsoft.com",
#           "AzureAppConfigurationEndpointResourceId": "https://azconfig.io",
#           "OperationalInsightsEndpoint": "https://api.loganalytics.io/v1",
#           "AzureSynapseAnalyticsEndpointSuffix": "dev.azuresynapse.net",
#           "AzureAttestationServiceEndpointResourceId": "https://attest.azure.net",
#           "AzureSynapseAnalyticsEndpointResourceId": "https://dev.azuresynapse.net",
#           "OperationalInsightsEndpointResourceId": "https://api.loganalytics.io",
#           "AzureAppConfigurationEndpointSuffix": "azconfig.io",
#           "AzurePurviewEndpointResourceId": "https://purview.azure.net",
#           "AzureAnalysisServicesEndpointSuffix": "asazure.windows.net",
#           "ManagedHsmServiceEndpointResourceId": "https://managedhsm.azure.net",
#           "AnalysisServicesEndpointResourceId": "https://region.asazure.windows.net",
#           "AzurePurviewEndpointSuffix": "purview.azure.net"