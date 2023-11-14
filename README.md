# Tools for Azure
## Habu 
- Azure Enumeration - will be deprecated soon since MS is deprecating the AzureAD PowerShell Module
- Will need to rewrite this using the Az and Microsoft.Graph PowerShell Modules
## Get-AzRefreshToken 
- Fetch Azure refresh or access token via Save-AzContext to use with AzureHound
## AZDL 
- Mostly automated device login flow using a Python script to fetch a refresh or access token to use with AzureHound
- https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code
## ADROPC
- Python script to obtain an access or refresh token via username and password. This will not work with an account that is part of an Azure hybrid setup with identity federation (ADFS, etc.)
- https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth-ropc
## Grifter
- Steal Azure access and refresh tokens via the DPAPI protected (currentuser context) $env:HOMEPATH/.azure/msal_token_cache.bin file
