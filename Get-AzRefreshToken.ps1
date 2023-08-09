function Get-AzRefreshToken {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$false)]
        [string]$UPN = "$($env:USERNAME)@$($env:USERDNSDOMAIN)",

        [Parameter(Mandatory=$false)]
        [string]$ContextFileName = "$($UPN)-AZTokens.txt",

        [Parameter(Mandatory=$false)]
        [string]$Tenant = "$($env:USERDOMAIN).onmicrosoft.com"
    )


    # Get Password
    $Password = Read-Host "Enter Password" -AsSecureString

    $AZCredential = [System.Management.Automation.PSCredential]::new($UPN, $Password)

    try {
        if(Connect-AzAccount -Tenant $Tenant -Credential $AZCredential){

            Save-AzContext -Path $ContextFileName

            $Context = (Get-Content $ContextFileName -Raw | ConvertFrom-Json)
            $tuidinfo = ((Get-Content $ContextFileName -Raw | ConvertFrom-Json).Contexts | Get-Member -MemberType NoteProperty).Name
            
            if($tuidinfo.GetType().Name -eq "Object[]") { $count = 0; $tuidinfo | %{ Write-Host ([System.String]::Format("[{0}] {1}", $count, $_)); $count++ }}

            $Option = Read-Host "`nSelect option"
            $tuidinfo = $tuidinfo[$Option]
            
            $TokenData = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Context.Contexts.$tuidinfo.TokenCache.CacheData))
            $RTID = (($TokenData | ConvertFrom-Json).RefreshToken | Get-Member -MemberType NoteProperty).Name

            if($RTID.GetType().Name -eq "Object[]") { $RTID = $RTID[$Option] }

            $secret = ($TokenData | ConvertFrom-Json).RefreshToken.$RTID.secret
        
            if($secret) {
                Set-Clipboard $secret
                $Output = [string]::Format("-----Refresh Token obtained and copied to clipboard------`n`n{0}`n", $secret)
                Write-Host $Output
                Remove-Item $ContextFileName -Force
            } else {
                Write-Host "[X]: The refresh token could not be obtained!" -BackgroundColor Black -ForegroundColor Red
            }
            
        }
        else {
            Write-Host "[i]: There was an error during authentication. Please try again." -ForegroundColor Yellow -BackgroundColor Black
        }

    } catch [Microsoft.Azure.Commands.Profile.ConnectAzureRmAccountCommand] {
        Write-Host "[X]: The UPN, password or tenant provided is not valid!" -ForegroundColor Red -BackgroundColor Yellow
    }
}
