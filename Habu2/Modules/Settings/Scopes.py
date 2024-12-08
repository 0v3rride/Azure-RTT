# scopes v2.0/resources v1.0 - https://learn.microsoft.com/en-us/entra/identity-platform/scopes-oidc
# https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide
# https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/managed-identities-status#azure-services-that-support-azure-ad-authentication
# https://graphpermissions.merill.net/permission/

Scope = {
    "graph": "https://graph.microsoft.com//.default openid profile offline_access", # AADGraph API https://graph.windows.net - https://stackoverflow.com/questions/62513980/whats-the-difference-between-graph-windows-net-and-graph-microsoft-com
    "aad graph": "https://graph.windows.net//.default openid profile offline_access",
    "management": "https://management.azure.com//.default openid profile offline_access", # or https://management.core.windows.net//.default
    "windows net management api": "https://management.core.windows.net//.default openid profile offline_access",
    "o365": "https://outlook.office365.com//.default openid profile offline_access", # or https://outlook.office.com Try different user agents with this when using requests (yes)
    "o3652": "https://outlook.office.com//.default openid profile offline_access",
    "teamsv1": "https://api.spaces.skype.com//.default openid profile offline_access",
    "teams": "https://teams.microsoft.com//.default openid profile offline_access",
    "substrate": "https://substrate.office.com//.default openid profile offline_access",
    "security": "https://security.microsoft.com//.default openid profile offline_access",
    "windowsdefenderatp": "https://api.securitycenter.microsoft.com//.default openid profile offline_access", 
    "compliance": "https://compliance.microsoft.com//.default openid profile offline_access",
    "mtp": "https://securitycenter.microsoft.com/mtp/.default openid profile offline_access",
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

    # Use with intune company portal client and broker auth
    "intune mdm": "https://enrollment.manage.micrsoft.com//.default openid profile offline_access",
    "intune": "https://manage.microsoft.com//.default openid profile offline_access",
    
    # "intune warehouse": "https://api.manage.microsoft.com//.default openid profile offline_access",
    # "Office": "https://www.office.com",
}

def GetScope(name):
    try:
        return Scope.get(name, name)
    except KeyError as ke:
        return name




#https://github.com/absolomb/FindMeAccess/blob/main/findmeaccess.py
#https://learn.microsoft.com/en-us/azure/security/fundamentals/azure-domains
#https://github.com/search?q=%2Fsecuritycenter%5C.microsoft%5C.com%5C%2Fmtp%5C%2F%2F&type=code
    #https://github.com/dirkjanm/ROADtools/blob/f63fa32392cfc78c1c2615b977d3e8a317dd90ca/roadtx/roadtools/roadtx/firstpartyscopes.json#L4184
    #https://github.com/maciejporebski/azure-ad-first-party-apps-permissions
        #https://github.com/search?q=%2Fccf4d8df-75ce-4107-8ea5-7afd618d4d8a%2F&type=code
            #https://github.com/f-bader/microsoft-info/tree/e42de7dcd94f3f6f56fce1d0083a61e1a060b8d0
    
    #https://github.com/simonxin/aadtokens/blob/48c3a1c9fb2d2c8b90953278d0405e06d651ae5c/src/AccessToken_utils.ps1#L235

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