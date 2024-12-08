# client teams, scope o365

import requests
import json
from rich.progress import track
from rich import print
import uuid
import base64

# https://github.com/Gerenios/AADInternals/blob/9c8fd15d2a853a6d6515da15d0d81bd3e0475f6d/Teams.ps1#L212
def SearchTeamUsers(accesstoken, keyword, useragent):
    url = f"https://substrate.office.com/search/api/v1/suggestions"
    headers = {"Authorization": f"Bearer {accesstoken}", "Content-Type": "application/json"}
    response = None
    users = []

    body = {
        "EntityRequests": [{
                "Query": {
                    "QueryString": keyword,
                    "DisplayQueryString": ""
                },
                "EntityType": "People",
                "Provenances": ["Mailbox", "Directory"],
                "From": 0,
                "Size": 500,
                
                "Fields": ["Id", "DisplayName", "EmailAddresses", "CompanyName", "JobTitle", "ImAddress", "UserPrincipalName", "ExternalDirectoryObjectId", "PeopleType", "PeopleSubtype", "ConcatenatedId", "Phones", "MRI"],

            }
        ],
        "Cvid": str(uuid.uuid4()),
        "AppName": "Microsoft Teams",
        "Scenario": {
            "Name": "staticbrowse"
        }
    }

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            results = json.loads(response.content.decode("utf-8"))
        
            if "Groups" in results:
                if len(results["Groups"]):
                    users = results["Groups"][0]["Suggestions"]
            
                if len(users) > 0:
                    response = users
            else:
                response = "[bold red][-][/bold red] No users found!"
        else:
            response = "[bold red][-][/bold red] No users found!"

    except Exception as e:
        response = e
    finally:
        return response
    
def SearchTeamMessages(accesstoken, userid, size, keyword, useragent):
    url = f"https://substrate.office.com/search/api/v2/query"
    headers = {"Authorization": f"Bearer {accesstoken}"}
    response = None
    resultSets = []
    queryString = "NOT (isClientSoftDeleted:TRUE)"

    if keyword:
        queryString = f"{keyword} AND NOT (isClientSoftDeleted:TRUE)"
    else:
        queryString = "NOT (isClientSoftDeleted:TRUE)"


    body = {
        "EntityRequests": [{
            "entityType": "Message",
            "contentSources": ["Teams"],
            "fields": ["*"],
            "propertySet": "Optimized",
            "query": {
                "queryString": queryString,
                "displayQueryString": keyword
            },
            "size": 5,
            "topResultsCount": 5
        }, {
            "contentSources": ["OneDriveBusiness"],
            "EnableQueryUnderstanding": False,
            "EnableSpeller": False,
            "EntityType": "File",
            "extendedQueries": [{
                "SearchProvider": "SharePoint",
                "Query": {
                    "SourceId": "",
                    "EnableQueryRules": False,
                    "TrimDuplicates": False,
                    "BypassResultTypes": True,
                    "ProcessBestBets": False,
                    "ProcessPersonalFavorites": False,
                    "EnableInterleaving": False,
                    "EnableMultiGeo": True,
                    "RankingModelId": "",
                    "Culture": 1033
                }
            }],
            "Fields": ["HitHighlightedSummary"],
            "From": 0,
            "HitHighlight": {
                "HitHighlightedProperties": ["HitHighlightedSummary"],
                "SummaryLength": 2048
            },
            "IdFormat": "EwsId",
            "ParserType": "None",
            "PropertySet": "Optimized",
            "Query": {
                "QueryString": keyword,
                "DisplayQueryString": keyword
            },
            "RefiningQueries": [{
                "RefinerString": "or(andnot(IsDocument:true,Title:or(OneNote_DeletedPages,OneNote_RecycleBin),SecondaryFileExtension:onetoc2,FileExtension:vtt,ContentClass:ExternalLink,and(ContentClass:STS_List_DocumentLibrary,SiteTemplateId:21),FileType:or(aspx,htm,html,mhtml),and(ContentTypeId:0x0101009D1CB255DA76424F860D91F20E6C4118*,PromotedState:2)),ContentTypeId:or(0x010100F3754F12A9B6490D9622A01FE9D8F012,0x0120D520A808*),SecondaryFileExtension:or(wmv,avi,mpg,asf,mp4,ogg,ogv,webm,mov),FileType:or(ai,bmp,dib,dst,emb,eps,gif,ico,jpeg,jpg,odg,png,rle,svg,tiff,webp,wmf,wpd))"
            }, {
                "RefinerString": "AllStorageProviderContexts:or(11,12)"
            }],
            "ResultsMerge": {
                "Type": "Interleaved"
            },
            "size": 3,
            "Sort": [{
                "Field": "PersonalScore",
                "SortDirection": "Desc"
            }]
        }, {
            "entityType": "People",
            "Filter": {
                "And": [{
                    "Or": [{
                        "Term": {
                            "PeopleType": "Person"
                        }
                    }, {
                        "Term": {
                            "PeopleType": "Other"
                        }
                    }]
                }, {
                    "Or": [{
                        "Term": {
                            "PeopleSubtype": "OrganizationUser"
                        }
                    }, {
                        "Term": {
                            "PeopleSubtype": "Guest"
                        }
                    }]
                }]
            },
            "contentSources": ["Exchange"],
            "query": {
                "queryString": keyword,
                "displayQueryString": keyword
            },
            "size": 8,
            "HitHighlight": {
                "HitHighlightedProperties": ["Responsibilities", "PreferredName", "JobTitle", "Skills", "PastProjects", "Schools", "Interests", "AboutMe", "OfficeNumber", "WorkEmail", "WorkPhone", "Department", "UserName"],
                "SummaryLength": 2048
            },
            "Fields": ["*"]
        }],
        "QueryAlterationOptions": {
            "EnableAlteration": True,
            "EnableSuggestion": True,
            "SupportedRecourseDisplayTypes": ["Suggestion"]
        },
        "cvid": str(uuid.uuid4()),
        "logicalId": "",
        "scenario": {
            "Dimensions": [{
                "DimensionName": "QueryType",
                "DimensionValue": "All"
            }, {
                "DimensionName": "FormFactor",
                "DimensionValue": "general.desktop.reactSearch"
            }],
            "Name": "powerbar"
        },
        "WholePageRankingOptions": {
            "EnableEnrichedRanking": True,
            "EnableLayoutHints": True,
            "SupportedSerpRegions": ["MainLine"]
        }
    }
    
    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.post(url, headers=headers, json=body)

        print(response.text)
        
        if response.status_code == 200:
            entitySets = json.loads(response.content.decode("utf-8"))["EntitySets"]

            for entitySet in entitySets:
                # print(entitySet["ResultSets"][0]["Provenance"])
                resultSets.append(entitySet["ResultSets"])
            
            if len(resultSets):
                response = resultSets
            
            # if len(sets) > 0:
            #     for set in sets:
            #         results = set["ResultSets"][0]["Results"]
            #         for result in results:
            #             print(result["ContentSource"])
                    # messageInfo = requests.get(url=f"https://graph.microsoft.com/v1.0/{userid}/messages/{message['Id']}", headers=headers)

                    # print(messageInfo.text)
        else:
            response = "[bold red][-][/bold red] No messages found!"

    except Exception as e:
        response = e
    finally:
        return response
    
# https://github.com/rvrsh3ll/TokenTactics/blob/a47308beddbd9084a6b7a3c23bca6c244475eb61/modules/OutlookEmailAbuse.ps1#L55
def OWADumpInbox(accesstoken, useragent):
    url = f"https://substrate.office.com/owa/"
    headers = {"Authorization": f"Bearer {accesstoken}", "Content-Type": "application/json"}
    response = None

    body = {
        "EntityRequests": [{
                "Query": {
                    "QueryString": "",
                    "DisplayQueryString": ""
                },
                "EntityType": "People",
                "Provenances": ["Mailbox", "Directory"],
                "From": 0,
                "Size": 500,
                
                "Fields": ["Id", "DisplayName", "EmailAddresses", "CompanyName", "JobTitle", "ImAddress", "UserPrincipalName", "ExternalDirectoryObjectId", "PeopleType", "PeopleSubtype", "ConcatenatedId", "Phones", "MRI"],

            }
        ],
        "Cvid": str(uuid.uuid4()),
        "AppName": "Microsoft Teams",
        "Scenario": {
            "Name": "staticbrowse"
        }
    }

    if useragent:
        headers.update({"User-Agent": useragent})

    try:
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            users = json.loads(response.content.decode("utf-8"))["Groups"][0]["Suggestions"]
            
            if len(users) > 0:
                response = users
        else:
            response = "[bold red][-][/bold red] No managed devices found!"

    except Exception as e:
        response = e
    finally:
        return response