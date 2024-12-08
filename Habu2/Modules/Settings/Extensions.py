# https://github.com/Gerenios/AADInternals/blob/9c8fd15d2a853a6d6515da15d0d81bd3e0475f6d/AzureManagementAPI_utils.ps1#L461
Extension = {
    "aad_iam": {"id": "74658136-14ec-4630-ad9b-26e160ff0fc6", "name": "Microsoft_AAD_IAM"},
    "aad_devices": {"id": "c40dfea8-483f-469b-aafe-642149115b3a", "name": "Microsoft_AAD_Devices"},
    "intune": {"id": "5926fc8e-304e-4f59-8bed-58ca97cc39a4", "name": "Microsoft_Intune"},
}

def GetExtension(name):
    try:
        return Extension.get(name, name)
    except KeyError as ke:
        return name
