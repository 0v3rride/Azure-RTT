import requests
import json
import io
import pathlib
from rich.progress import track
from base64 import b64decode


def ExtractAttachment(lootpath, subject, filename, rawbytes):
    subject = "".join(c for c in subject if c.isalpha() or c.isdigit() or c==' ').rstrip()

    pathlib.Path(f"{lootpath}{subject}").mkdir(parents=True, exist_ok=True)

    extractPath = f"{lootpath}{subject}/{filename}"
    file = io.open(f"{lootpath}{subject}/{filename}", mode="wb")

    try:
        file.write(b64decode(rawbytes))
    except Exception as e:
        print(e)
    finally:
        file.close()
        return extractPath
       

def GetAttachments(accesstoken, userid, lootpath, useragent, message):
    # List attachments and their ids for a specific message
    url = f"https://graph.microsoft.com/v1.0/users/{userid}/messages/{message['id']}/attachments"
    attachmentNames = []
    response = None
    headers={"Authorization": f"Bearer {accesstoken}"}
    
    if useragent:
       headers.update({"User-Agent": useragent})
    
    
    response = requests.get(url, headers=headers)
        
    if response.status_code == 200:
        results = json.loads(response.content.decode("utf-8"))["value"]
        attachments = []
        extractpaths = []

        if len(results) > 0:
            for attachment in results:
                attachments.append(attachment)
                attachmentNames.append([f"{lootpath}/{message['subject']}/{attachment['name']}"])

                # Get raw attachment bytes and save to a file
                response = requests.get(f"https://graph.microsoft.com/v1.0/users/{userid}/messages/{message['id']}/attachments/{attachment['id']}", headers=headers)

                if response.status_code == 200:
                    extractpaths.append(ExtractAttachment(lootpath, message["subject"], attachment["name"], json.loads(response.content.decode("utf-8"))["contentBytes"]))
        
        message.update({"attachments": attachments})
        message.update({"extractedAttachments": extractpaths})
        
    return message


def GetExchangeMessages(accesstoken, userid, extractattachments, lootpath, format, parameters, useragent):
    try:
        headers = {"Authorization": f"Bearer {accesstoken}"}
        results = None
        url = f"https://graph.microsoft.com/v1.0/users/{userid}/messages"

        if parameters:
            url = f"{url}?{parameters}" 
        
        if useragent:
            headers.update({"User-Agent": useragent})

        if format:
            headers.update({'Prefer': "outlook.body-content-type=\"{}\"".format(format)})

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            results = json.loads(response.content.decode("utf-8"))["value"]

            messages = []

            if isinstance(results, list):
                for message in track(results, "Gathering Exchange Messages..."):
                    if extractattachments:
                        message = GetAttachments(accesstoken, userid, lootpath, useragent, message)

                    messages.append(message)

                    # print("\n\n")
                    # print("=" * 175)

                    # # if extractattachments:
                    # #     attachments = GetAttachments(lootpath, accesstoken, useragent, email)
                    # #     if len(attachments) > 0:
                    # #         print("{}\n\n".format(tabulate.tabulate(attachments, tablefmt="simple", headers=["Attachments"])))
                        

                    # if "sender" in email:
                    #     if "emailAddress" in email["sender"]:
                    #         if "address" in email["sender"]["emailAddress"]:
                    #             print(f"Sender: {email['sender']['emailAddress']['address']}")

                    # print("-" * 175)
                    # print("\n")

                    # if "subject" in email:
                    #     print("Subject: {}".format(email["subject"]))

                    # print("\n")
                    # print("-" * 175)

                    # if "body" in email:
                    #     if "content" in email["body"]:
                    #         print(email["body"]["content"])
                    #         print("=" * 175)
            
            response = messages
        else:
            response = "No messages found!"

        
    except Exception as e:
        response = e
    finally:
        return response