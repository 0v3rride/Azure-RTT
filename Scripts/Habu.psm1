$Tenant = Read-Host -Prompt "Enter Tenant ID (guid, *.onmicrosoft.com or example.org)"
$Username = Read-Host -Prompt "Enter username to authenticate with";
[securestring]$Password = Read-Host -Prompt ([string]::Format("Enter password for user {0}", $Username)) -AsSecureString;
$Credential = New-Object System.Management.Automation.PSCredential($Username, $Password);

Connect-AzureAD -TenantId $Tenant -Credential $Credential;

################################
# Tenant Enumeration Functions #
################################
function Get-AZRDomain {    
    foreach ($domain in Get-AzureADDomain) {
        [PSCustomObject][Ordered]@{
            Domain                       = $domain.Name
            IsRoot                       = $domain.IsRoot
            IsInitial                    = $domain.IsInitial
            IsVerified                   = $domain.IsVerified
            IsDefault                    = $domain.IsDefault
            IsDefaultForCloudRedirection = $domain.IsDefaultForCloudRedirection
            IsAdminManaged               = $domain.IsAdminManaged
            State                        = $domain.State
            AuthType                     = $domain.AuthenticationType
        }
    }
}

function Get-AZRExtension {
    Get-AzureADExtensionProperty;
}

##############################
# User Enumeration Functions #
##############################
function Get-AZRUser {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "BySearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByUPN")]
        [string] $UPN = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID) -and [string]::IsNullOrEmpty($UPN)) {
        foreach ($user in (Get-AzureADUser -All $True)) {
            $user | Add-Member -NotePropertyName "Manager" -NotePropertyValue (Get-AzureADUserManager -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "Subordinate" -NotePropertyValue (Get-AzureADUserDirectReport -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "onPremisesDistinguishedName" -NotePropertyValue (Get-AzureADUserExtension -ObjectId $user.ObjectId).onPremisesDistinguishedName
            $user 
        }
    }
    elseif ($SearchString) {
        foreach ($user in (Get-AzureADUser -All $True -SearchString $SearchString)) {
            $user | Add-Member -NotePropertyName "Manager" -NotePropertyValue (Get-AzureADUserManager -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "Subordinate" -NotePropertyValue (Get-AzureADUserDirectReport -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "onPremisesDistinguishedName" -NotePropertyValue (Get-AzureADUserExtension -ObjectId $user.ObjectId).onPremisesDistinguishedName
            $user 
        }
    }
    elseif ($ObjectID) {
        foreach ($user in (Get-AzureADUser -ObjectId ("{0}" -f $ObjectID))) {
            $user | Add-Member -NotePropertyName "Manager" -NotePropertyValue (Get-AzureADUserManager -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "Subordinate" -NotePropertyValue (Get-AzureADUserDirectReport -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "onPremisesDistinguishedName" -NotePropertyValue (Get-AzureADUserExtension -ObjectId $user.ObjectId).onPremisesDistinguishedName
            $user 
        }
    }
    elseif ($UPN) {
        foreach ($user in (Get-AzureADUser -ObjectId ("{0}" -f $UPN))) {
            $user | Add-Member -NotePropertyName "Manager" -NotePropertyValue (Get-AzureADUserManager -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "Subordinate" -NotePropertyValue (Get-AzureADUserDirectReport -ObjectId $user.ObjectId).UserPrincipalName
            $user | Add-Member -NotePropertyName "onPremisesDistinguishedName" -NotePropertyValue (Get-AzureADUserExtension -ObjectId $user.ObjectId).onPremisesDistinguishedName
            $user 
        }
    }
}

function Get-AZRUserAppRole {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByUPN")]
        [string] $UPN = $null
    )

    if ($ObjectID) {
        Get-AzureADUserAppRoleAssignment -All $True -ObjectId ("{0}" -f $ObjectID) 
    }
    elseif ($UPN) {
        Get-AzureADUserAppRoleAssignment -All $True -ObjectId ("{0}" -f $UPN) 
    }
}

function Get-AZRUserDirectoryRole {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "SearchString")]
        [string] $SearchString = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID)) {
        foreach ($role in (Get-AzureADDirectoryRole)) {
            foreach ($user in (Get-AzureADDirectoryRoleMember -ObjectId $role.ObjectId).UserPrincipalName) {
                [PSCustomObject][Ordered]@{
                    RoleName        = $role.DisplayName
                    RoleDescription = $role.Description
                    RoleId          = $role.ObjectId
                    IsSystem        = $role.IsSystem
                    Disabled        = $role.RoleDisabled
                    MemberUPN       = $user
                }
            }
        }
    }
    elseif ($ObjectID) {
        foreach ($role in (Get-AzureADDirectoryRole -ObjectId $ObjectID)) {
            foreach ($user in (Get-AzureADDirectoryRoleMember -ObjectId $role.ObjectId).UserPrincipalName) {
                [PSCustomObject][Ordered]@{
                    RoleName        = $role.DisplayName
                    RoleDescription = $role.Description
                    RoleId          = $role.ObjectId
                    IsSystem        = $role.IsSystem
                    Disabled        = $role.RoleDisabled
                    MemberUPN       = $user
                }
            }
        }
    }
    elseif ($SearchString) {
        foreach ($role in (Get-AzureADDirectoryRole | Where-Object { $_.DisplayName -like "*$SearchString*" })) {
            foreach ($user in (Get-AzureADDirectoryRoleMember -ObjectId $role.ObjectId).UserPrincipalName) {
                [PSCustomObject][Ordered]@{
                    RoleName        = $role.DisplayName
                    RoleDescription = $role.Description
                    RoleId          = $role.ObjectId
                    IsSystem        = $role.IsSystem
                    Disabled        = $role.RoleDisabled
                    MemberUPN       = $user
                }
            }
        }
    }
}

function Get-AZRUserCreatedObject {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByUPN")]
        [string] $UPN = $null
    )

    if ($ObjectID) {
        Get-AzureADUserCreatedObject -All $true -ObjectId ("{0}" -f $ObjectID) 
    }
    elseif ($UPN) {
        Get-AzureADUserCreatedObject -All $true -ObjectId ("{0}" -f $UPN) 
    }
}

function Get-AZRUserGroupMembership {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByUPN")]
        [string] $UPN = $null
    )

    if ($ObjectID) {
        Get-AzureADUserMembership -ObjectId ("{0}" -f $ObjectID) 
    }
    elseif ($UPN) {
        Get-AzureADUserMembership -ObjectId ("{0}" -f $UPN) 
    }
}

function Get-AZRUserDevice {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByUPN")]
        [string] $UPN = $null
    )

    if ($ObjectID) {
        Get-AzureADUserOwnedDevice -ObjectId ("{0}" -f $ObjectID) 
    }
    elseif ($UPN) {
        Get-AzureADUserOwnedDevice -ObjectId ("{0}" -f $UPN) 
    }
}

###############################
# Group Enumeration Functions #
###############################
function Get-AZRGroup {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "BySearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID)) {
        foreach ($group in (Get-AzureADGroup -All $True)) {
            [PSCustomObject][Ordered]@{
                DisplayName                  = $group.DisplayName
                Description                  = $group.Description
                ObjectId                     = $group.ObjectId
                OnPremisesSecurityIdentifier = $group.OnPremisesSecurityIdentifier
                DirSyncEnabled               = $group.DirSyncEnabled
                DirSyncTime                  = $group.DirSyncOn
                HasMail                      = $group.MailEnabled
                MailAddress                  = $group.Mail
            } 
        }
    }
    elseif ($SearchString) {
        foreach ($group in (Get-AzureADGroup -All $True -SearchString $SearchString)) {
            [PSCustomObject][Ordered]@{
                DisplayName                  = $group.DisplayName
                Description                  = $group.Description
                ObjectId                     = $group.ObjectId
                OnPremisesSecurityIdentifier = $group.OnPremisesSecurityIdentifier
                DirSyncEnabled               = $group.DirSyncEnabled
                DirSyncTime                  = $group.DirSyncOn
                HasMail                      = $group.MailEnabled
                MailAddress                  = $group.Mail
            } 
        }
    }
    elseif ($ObjectID) {
        foreach ($group in (Get-AzureADGroup -ObjectId ("{0}" -f $ObjectID))) {
            [PSCustomObject][Ordered]@{
                DisplayName                  = $group.DisplayName
                Description                  = $group.Description
                ObjectId                     = $group.ObjectId
                OnPremisesSecurityIdentifier = $group.OnPremisesSecurityIdentifier
                DirSyncEnabled               = $group.DirSyncEnabled
                DirSyncTime                  = $group.DirSyncOn
                HasMail                      = $group.MailEnabled
                MailAddress                  = $group.Mail
            } 
        }
    }
}

function Get-AZRGroupMember {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "BySearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID)) {
        foreach ($group in (Get-AzureADGroup -All $True)) {
            foreach ($member in (Get-AzureADGroupMember -All $True -ObjectId $group.ObjectId)) {
                [PSCustomObject][Ordered]@{
                    GroupName         = $group.DisplayName
                    GroupId           = $group.ObjectId
                    GroupDescription  = $group.Description
                    MemberUPN         = $member.UserPrincipalName
                    MemberSID         = $member.OnPremisesSecurityIdentifier
                    MemberOID         = $member.ObjectId
                    MemberEmail       = $member.Mail
                    MemberDepartment  = $member.Department
                    MemberPhoneNumber = $member.TelephoneNumber
                    MemberMobile      = $member.Mobile
                    DirSyncOn         = $member.DirSyncEnabled
                    PasswordPolicies  = $member.PasswordPolicies
                } 
            }
        }
    }
    elseif ($SearchString) {
        foreach ($group in (Get-AzureADGroup -All $True | Where-Object { $_.DisplayName -like "*$SearchString*" })) {
            foreach ($member in (Get-AzureADGroupMember -All $True -ObjectId $group.ObjectId)) {
                [PSCustomObject][Ordered]@{
                    GroupName         = $group.DisplayName
                    GroupId           = $group.ObjectId
                    GroupDescription  = $group.Description
                    MemberUPN         = $member.UserPrincipalName
                    MemberSID         = $member.OnPremisesSecurityIdentifier
                    MemberOID         = $member.ObjectId
                    MemberEmail       = $member.Mail
                    MemberDepartment  = $member.Department
                    MemberPhoneNumber = $member.TelephoneNumber
                    MemberMobile      = $member.Mobile
                    DirSyncOn         = $member.DirSyncEnabled
                    PasswordPolicies  = $member.PasswordPolicies
                } 
            }
        }
    }
    elseif ($ObjectID) {
        foreach ($member in (Get-AzureADGroupMember -All $True -ObjectId $ObjectID)) {
            [PSCustomObject][Ordered]@{
                GroupName         = (Get-AzureADGroup -ObjectId $ObjectID).DisplayName
                GroupId           = (Get-AzureADGroup -ObjectId $ObjectID).ObjectId
                GroupDescription  = (Get-AzureADGroup -ObjectId $ObjectID).Description
                MemberUPN         = $member.UserPrincipalName
                MemberSID         = $member.OnPremisesSecurityIdentifier
                MemberOID         = $member.ObjectId
                MemberEmail       = $member.Mail
                MemberDepartment  = $member.Department
                MemberPhoneNumber = $member.TelephoneNumber
                MemberMobile      = $member.Mobile
                DirSyncOn         = $member.DirSyncEnabled
                PasswordPolicies  = $member.PasswordPolicies
            } 
        }
    }
}

function Get-AZRGroupRole {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null
    )

    if ([string]::IsNullOrEmpty($ObjectID)) {
        foreach ($group in (Get-AzureADGroup -All $True)) {
            Get-AzureADGroupAppRoleAssignment -All $True -ObjectId $group.ObjectId 
        }
    }
    elseif ($ObjectID) {
        Get-AzureADGroupAppRoleAssignment -All $True -ObjectId $ObjectID  
    }
}

############################
# Azure Device Enumeration #
############################
function Get-AZRDevice {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "BySearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "UPN")]
        [string] $DisplayName = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID) -and [string]::IsNullOrEmpty($UPN)) {
        foreach ($device in (Get-AzureADDevice -All $True)) {
            [PSCustomObject][Ordered]@{
                DeviceName             = $device.DisplayName
                ObjectId               = $device.ObjectId
                DeviceID               = $device.DeviceID
                RegisteredOwner        = (Get-AzureADDeviceRegisteredOwner -ObjectId $device.ObjectId).UserPrincipalName
                RegisteredUser         = (Get-AzureADDeviceRegisteredUser -ObjectId $device.ObjectId).UserPrincipalName
                AproxLastLogonTime     = $device.ApproximateLastLogonTimeStamp
                OperatingSystem        = $device.DeviceOSType
                OperatingSystemVersion = $device.DeviceOSVersion
            } 
        }
    }
    elseif ($SearchString) {
        foreach ($device in (Get-AzureADDevice -All $True -SearchString $SearchString)) {
            [PSCustomObject][Ordered]@{
                DeviceName             = $device.DisplayName
                ObjectId               = $device.ObjectId
                DeviceID               = $device.DeviceID
                RegisteredOwner        = (Get-AzureADDeviceRegisteredOwner -ObjectId $device.ObjectId).UserPrincipalName
                RegisteredUser         = (Get-AzureADDeviceRegisteredUser -ObjectId $device.ObjectId).UserPrincipalName
                AproxLastLogonTime     = $device.ApproximateLastLogonTimeStamp
                OperatingSystem        = $device.DeviceOSType
                OperatingSystemVersion = $device.DeviceOSVersion
            } 
        }
    }
    elseif ($ObjectID) {
        foreach ($device in (Get-AzureADDevice -ObjectId $ObjectID)) {
            [PSCustomObject][Ordered]@{
                DeviceName             = $device.DisplayName
                ObjectId               = $device.ObjectId
                DeviceID               = $device.DeviceID
                RegisteredOwner        = (Get-AzureADDeviceRegisteredOwner -ObjectId $device.ObjectId).UserPrincipalName
                RegisteredUser         = (Get-AzureADDeviceRegisteredUser -ObjectId $device.ObjectId).UserPrincipalName
                AproxLastLogonTime     = $device.ApproximateLastLogonTimeStamp
                OperatingSystem        = $device.DeviceOSType
                OperatingSystemVersion = $device.DeviceOSVersion
            } 
        }
    }
}

#################################
# Azure Application Enumeration #
#################################
function Get-AZRApplication {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "BySearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID)) {
        foreach ($app in (Get-AzureADApplication -All $True)) {
            [PSCustomObject][Ordered]@{
                AppName                    = $app.DisplayName
                AppOID                     = $app.ObjectId
                AppAID                     = $app.AppId
                AppOwner                   = (Get-AzureADApplicationOwner -ObjectId $app.ObjectId).UserPrincipalName
                GuestSignIn                = $app.AllowGuestsSignIn
                PassThroughUsers           = $app.AllowPassthroughUsers
                AppRoles                   = $app.AppRoles
                GroupMembershipClaims      = $app.GroupMembershipClaims
                AvailableToOtherTenants    = $app.AvailableToOtherTenants
                DeviceAuthOnly             = $app.IsDeviceOnlyAuthSupported
                OrgRestrictions            = $app.OrgRestrictions
                Domain                     = $app.Domain
                ServiceEndpoint            = (Get-AzureADApplicationServiceEndpoint -ObjectId $app.ObjectId)
                AppExtension               = (Get-AzureADApplicationExtensionProperty -ObjectId $app.ObjectId)
                AppPassCustomKeyIdentifier = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).CustomKeyIdentifier
                AppPassKID                 = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).KeyId
                AppPassValue               = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).Value
                AppPassStartDate           = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).StartDate
                AppPassEndDate             = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).EndDate
            }
        }
    }
    elseif ($SearchString) {
        foreach ($appinstance in (Get-AzureADApplication -All $True | Where-Object { $_.DisplayName -like "*$SearchString*" })) {
            foreach ($app in (Get-AzureADApplication -ObjectId $appinstance.ObjectId)) {
                [PSCustomObject][Ordered]@{
                    AppName                    = $app.DisplayName
                    AppOID                     = $app.ObjectId
                    AppAID                     = $app.AppId
                    AppOwner                   = (Get-AzureADApplicationOwner -ObjectId $app.ObjectId).UserPrincipalName
                    GuestSignIn                = $app.AllowGuestsSignIn
                    PassThroughUsers           = $app.AllowPassthroughUsers
                    AppRoles                   = $app.AppRoles
                    GroupMembershipClaims      = $app.GroupMembershipClaims
                    AvailableToOtherTenants    = $app.AvailableToOtherTenants
                    DeviceAuthOnly             = $app.IsDeviceOnlyAuthSupported
                    OrgRestrictions            = $app.OrgRestrictions
                    Domain                     = $app.Domain
                    ServiceEndpoint            = (Get-AzureADApplicationServiceEndpoint -ObjectId $app.ObjectId)
                    AppExtension               = (Get-AzureADApplicationExtensionProperty -ObjectId $app.ObjectId)
                    AppPassCustomKeyIdentifier = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).CustomKeyIdentifier
                    AppPassKID                 = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).KeyId
                    AppPassValue               = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).Value
                    AppPassStartDate           = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).StartDate
                    AppPassEndDate             = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).EndDate
                }
            }
        }
    }
    elseif ($ObjectID) {
        foreach ($app in  Get-AzureADApplication -ObjectId $ObjectID) {
            [PSCustomObject][Ordered]@{
                AppName                    = $app.DisplayName
                AppOID                     = $app.ObjectId
                AppAID                     = $app.AppId
                AppOwner                   = (Get-AzureADApplicationOwner -ObjectId $app.ObjectId).UserPrincipalName
                GuestSignIn                = $app.AllowGuestsSignIn
                PassThroughUsers           = $app.AllowPassthroughUsers
                AppRoles                   = $app.AppRoles
                GroupMembershipClaims      = $app.GroupMembershipClaims
                AvailableToOtherTenants    = $app.AvailableToOtherTenants
                DeviceAuthOnly             = $app.IsDeviceOnlyAuthSupported
                OrgRestrictions            = $app.OrgRestrictions
                Domain                     = $app.Domain
                ServiceEndpoint            = (Get-AzureADApplicationServiceEndpoint -ObjectId $app.ObjectId)
                AppExtension               = (Get-AzureADApplicationExtensionProperty -ObjectId $app.ObjectId)
                AppPassCustomKeyIdentifier = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).CustomKeyIdentifier
                AppPassKID                 = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).KeyId
                AppPassValue               = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).Value
                AppPassStartDate           = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).StartDate
                AppPassEndDate             = (Get-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId).EndDate
            }
        }
    }
}

#######################################
# Azure Service Principal Enumeration #
#######################################
function Get-AZRServicePrincipal {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "BySearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null
    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID)) {
        foreach ($serviceprincipal in (Get-AzureADServicePrincipal -All $True)) {
            [PSCustomObject][Ordered]@{
                SPName                = $serviceprincipal.DisplayName
                SPID                  = $serviceprincipal.ObjectId
                SPNs                  = $serviceprincipal.ServicePrincipalNames
                Roles                 = $serviceprincipal.AppRoles
                ReplyUrls             = $serviceprincipal.ReplyUrls
                PublisherName         = $serviceprincipal.PublisherName
                Owner                 = (Get-AzureADServicePrincipalOwner -ObjectId $serviceprincipal.ObjectId).UserPrincipalName
                MembershipName        = (Get-AzureADServicePrincipalMembership -ObjectId $serviceprincipal.ObjectId).DisplayName
                MembershipDescription = (Get-AzureADServicePrincipalMembership -ObjectId $serviceprincipal.ObjectId).Description
                OwnedObject           = (Get-AzureADServicePrincipalOwnedObject -ObjectId $serviceprincipal.ObjectId).DisplayName
                CreatedObject         = (Get-AzureADServicePrincipalCreatedObject -ObjectId $serviceprincipal.ObjectId).DisplayName
                KeyId                 = (Get-AzureADServicePrincipalPasswordCredential -ObjectId $serviceprincipal.ObjectId).KeyId
                KeyValue              = (Get-AzureADServicePrincipalPasswordCredential -ObjectId $serviceprincipal.ObjectId).Value
                Type                  = $serviceprincipal.ServicePrincipalType
            } 
        }
    }
    elseif ($SearchString) {
        foreach ($serviceprincipal in (Get-AzureADServicePrincipal -All $True -SearchString $SearchString)) {
            [PSCustomObject][Ordered]@{
                SPName                = $serviceprincipal.DisplayName
                SPID                  = $serviceprincipal.ObjectId
                SPNs                  = $serviceprincipal.ServicePrincipalNames
                Roles                 = $serviceprincipal.AppRoles
                ReplyUrls             = $serviceprincipal.ReplyUrls
                PublisherName         = $serviceprincipal.PublisherName
                Owner                 = (Get-AzureADServicePrincipalOwner -ObjectId $serviceprincipal.ObjectId).UserPrincipalName
                MembershipName        = (Get-AzureADServicePrincipalMembership -ObjectId $serviceprincipal.ObjectId).DisplayName
                MembershipDescription = (Get-AzureADServicePrincipalMembership -ObjectId $serviceprincipal.ObjectId).Description
                OwnedObject           = (Get-AzureADServicePrincipalOwnedObject -ObjectId $serviceprincipal.ObjectId).DisplayName
                CreatedObject         = (Get-AzureADServicePrincipalCreatedObject -ObjectId $serviceprincipal.ObjectId).DisplayName
                KeyId                 = (Get-AzureADServicePrincipalPasswordCredential -ObjectId $serviceprincipal.ObjectId).KeyId
                KeyValue              = (Get-AzureADServicePrincipalPasswordCredential -ObjectId $serviceprincipal.ObjectId).Value
                Type                  = $serviceprincipal.ServicePrincipalType
            } 
        }
    }
    elseif ($ObjectID) {
        foreach ($serviceprincipal in (Get-AzureADServicePrincipal -ObjectId $ObjectID)) {
            [PSCustomObject][Ordered]@{
                SPName                = $serviceprincipal.DisplayName
                SPID                  = $serviceprincipal.ObjectId
                SPNs                  = $serviceprincipal.ServicePrincipalNames
                Roles                 = $serviceprincipal.AppRoles
                ReplyUrls             = $serviceprincipal.ReplyUrls
                PublisherName         = $serviceprincipal.PublisherName
                Owner                 = (Get-AzureADServicePrincipalOwner -ObjectId $serviceprincipal.ObjectId).UserPrincipalName
                MembershipName        = (Get-AzureADServicePrincipalMembership -ObjectId $serviceprincipal.ObjectId).DisplayName
                MembershipDescription = (Get-AzureADServicePrincipalMembership -ObjectId $serviceprincipal.ObjectId).Description
                OwnedObject           = (Get-AzureADServicePrincipalOwnedObject -ObjectId $serviceprincipal.ObjectId).DisplayName
                CreatedObject         = (Get-AzureADServicePrincipalCreatedObject -ObjectId $serviceprincipal.ObjectId).DisplayName
                KeyId                 = (Get-AzureADServicePrincipalPasswordCredential -ObjectId $serviceprincipal.ObjectId).KeyId
                KeyValue              = (Get-AzureADServicePrincipalPasswordCredential -ObjectId $serviceprincipal.ObjectId).Value
                Type                  = $serviceprincipal.ServicePrincipalType
            } 
        }
    }
}

function Get-AZRServicePrincipalAppRole {
    [CmdletBinding(DefaultParameterSetName = "ByObjectID")]
    param(
        [Parameter(Mandatory = $false, ParameterSetName = "ByObjectID")]
        [string] $ObjectID = $null,
        [Parameter(Mandatory = $false, ParameterSetName = "SearchString")]
        [string] $SearchString = $null,
        [Parameter(Mandatory = $false)]
        [switch] $DoNotShowNull

    )

    if ([string]::IsNullOrEmpty($SearchString) -and [string]::IsNullOrEmpty($ObjectID)) {
        foreach ($sp in (Get-AzureADServicePrincipal -All $true)) {
            if ($DoNotShowNull) {
                if ((Get-AzureADServiceAppRoleAssignment -All $true -ObjectId $sp.ObjectId) -ne $null) {
                    [PSCustomObject][Ordered]@{
                        ResourceDisplayName  = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceDisplayName
                        PrincipalDisplayName = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalDisplayName
                        CreationTimestamp    = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).CreationTimestamp
                        PrincipalType        = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalType
                        ObjectId             = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ObjectId
                        ResourceId           = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceId
                    }
                }
                else {
                    [PSCustomObject][Ordered]@{
                        ResourceDisplayName  = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceDisplayName
                        PrincipalDisplayName = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalDisplayName
                        CreationTimestamp    = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).CreationTimestamp
                        PrincipalType        = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalType
                        ObjectId             = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ObjectId
                        ResourceId           = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceId
                    }
                }
            
            }
        }
    }
    elseif ($ObjectID) {
        foreach ($sp in (Get-AzureADServicePrincipal -ObjectId $ObjectID)) {
            [PSCustomObject][Ordered]@{
                ResourceDisplayName  = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceDisplayName
                PrincipalDisplayName = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalDisplayName
                CreationTimestamp    = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).CreationTimestamp
                PrincipalType        = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalType
                ObjectId             = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ObjectId
                ResourceId           = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceId
            }
        }
    }
    elseif ($SearchString) {
        foreach ($sp in (Get-AzureADServicePrincipal -All $true | Where-Object { $_.DisplayName -like "*$SearchString*" })) {
            if ($DoNotShowNull) {
                if ((Get-AzureADServiceAppRoleAssignment -All $true -ObjectId $sp.ObjectId) -ne $null) {
                    [PSCustomObject][Ordered]@{
                        ResourceDisplayName  = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceDisplayName
                        PrincipalDisplayName = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalDisplayName
                        CreationTimestamp    = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).CreationTimestamp
                        PrincipalType        = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalType
                        ObjectId             = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ObjectId
                        ResourceId           = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceId
                    }
                }
                else {
                    [PSCustomObject][Ordered]@{
                        ResourceDisplayName  = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceDisplayName
                        PrincipalDisplayName = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalDisplayName
                        CreationTimestamp    = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).CreationTimestamp
                        PrincipalType        = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).PrincipalType
                        ObjectId             = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ObjectId
                        ResourceId           = (Get-AzureADServiceAppRoleAssignment -ObjectId $sp.ObjectId).ResourceId
                    }
                }
            }
        }
    }
}
