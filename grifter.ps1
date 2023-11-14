$fileBytes = [System.IO.File]::ReadAllBytes("$($env:HOMEDRIVE)\Users\$($env:USERNAME)\.azure\msal_token_cache.bin")
$dFileBytes = [System.Security.Cryptography.ProtectedData]::Unprotect($fileBytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
$uFile = [System.Text.Encoding]::UTF8.GetString($dFileBytes)

$uFile
