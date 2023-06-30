#!/usr/bin/env python
"""
GoBridge: An SMTP to GMail API service
This tool will allow you to host an SMTP server that will accept emails and directly INSERT them into users' inboxes, bypassing any filtering.
This is achieved by using the Google Workspace API; and specifically the 'users.messages.insert' endpoint.

You will need to authorize your service account client via the Google Workspace admin console, and save the 'service_secret.json' file
to the working directory. This will give permission to impersonate any user and insert the email into their inbox.
Authorizing a service account to access data on behalf of users in a domain is sometimes referred to as "delegating domain-wide authority"
to a service account.

References:
https://developers.google.com/gmail/api/reference/rest/v1/users.messages/insert
https://console.cloud.google.com/iam-admin/serviceaccounts
https://developers.google.com/identity/protocols/oauth2/service-account#creatinganaccount
https://developers.google.com/cloud-search/docs/guides/delegation#python
https://stackoverflow.com/questions/42438902/gmail-api-user-impersonation-python

"""
__author__ = "Glenn Wilkinson"
__email__ = "glennzw@protonmail.com"
__license__ = "MIT"


# Need to upgrade to aiosmtpd as smtpd is deprecated and will be removed in Python 3.12
# In the meantime let's suppress the warning
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#Libraries for Google API
import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import oauth2client 
from googleapiclient.errors import HttpError
import json
# Libraries for SMTP server
import smtpd
import asyncore
import base64
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read('config.ini')

CLIENT_SECRET_FILE = config.get('GOBRIDGE', 'ClientSecretFile')
SMTP_PORT = config.getint('GOBRIDGE', 'SMTPPort')
SMTP_INTERFACE = config.get('GOBRIDGE', 'SMTPInterface')
LABELS = config.get('GOBRIDGE', 'Labels').split(',')

scopes = ["https://www.googleapis.com/auth/gmail.insert"]

splash = """
   _____       ____       _     _            
  / ____|     |  _ \     (_)   | |           
 | |  __  ___ | |_) |_ __ _  __| | __ _  ___ 
 | | |_ |/ _ \|  _ <| '__| |/ _` |/ _` |/ _ \\
 | |__| | (_) | |_) | |  | | (_| | (_| |  __/
  \_____|\___/|____/|_|  |_|\__,_|\__, |\___|
                                   __/ |     
                                  |___/

                     SMTP to GMail API Server
                     V0.1
"""

# SMTP server
class SMTPServer(smtpd.SMTPServer):
    """An SMTP server"""
    def __init__(*args, **kwargs):
        print(splash)
        print("[+] Running GoBridge SMTP server on port ", SMTP_PORT)
        smtpd.SMTPServer.__init__(*args, **kwargs)

    def process_message(self, peer, mailfrom, rcpttos, data, mail_options=None, rcpt_options=None):
        """Take emails sent over SMTP and insert them into the user's mailbox"""
        # NB If any of the addresses in rcpttos fail the function will return
        for rcptto in rcpttos:
            try:
                message = {'labelIds': LABELS, 'raw': base64.b64encode(data).decode('utf-8')}
                delegated_credentials = credentials.create_delegated(rcptto)
                http_auth = delegated_credentials.authorize(httplib2.Http())
                service = discovery.build('gmail', 'v1', http=http_auth)
                try:
                    result = service.users().messages().insert(userId="me", body=message).execute()
                    print(F'[+] Successfully inserted message for {rcptto} with Id: {result["id"]}')
                except HttpError as err:
                    if err.resp.get('content-type', '').startswith('application/json'):
                        reason = json.loads(err.content).get('error').get('message')
                        print(F'[!] An error occurred inserting mail for {rcptto}: {reason}')
                        return(F'554 {reason}')
                    print(F'[!] An error occurred inserting mail for {rcptto}')
                    return '554 Unahndled error'
                except oauth2client.client.HttpAccessTokenRefreshError as err:
                    print(F'[!] An error occurred inserting mail for {rcptto}: {err}')
                    return(F'554 {err}')
            except Exception as error:
                print(F'[!] An error occurred inserting mail for {rcptto}: {error}')
                #raise error
                return '554 Unahndled error'

if __name__ == "__main__":    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, scopes)
    http = credentials.authorize(httplib2.Http())
    smtp_server = SMTPServer((SMTP_INTERFACE, SMTP_PORT), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        smtp_server.close()