# GoBridge

GoBridge is an SMTP to GMail API service. It will allow you to host an SMTP server that will accept emails and directly INSERT them into users' inboxes, bypassing any filtering. This is achieved by using the GMail API; and specifically the `users.messages.insert` endpoint.

You will need to create and authorize a service account, save the `service_secret.json` file to the working directory, and delegate domain-wide authority for the service account. This will give permission to impersonate any user and insert the email into their inbox. For a step by step list of instructions please see [GMailSetup.md](GMailSetupDocumentation/GMailSetup.md)

## This stack
This stack changes some ways the core GoBridge applicaiton works in order to work within a docker compose stack.

## Configuration
Appropriate settings can be defined in the `config.json` file. The default values are and work securely as the service is behind a traefik reverse proxy:

```
     - SMTP_INTERFACE=0.0.0.0
     - SMTP_PORT=2500
     - LABELS=INBOX,UNREAD,IMPORTANT,STARRED
     - GOOGLE_SECRET=/service_secret
```

The `Labels` section refer to GMail labels - the default values ensure the email will be as visible as possible to the user.

Make sure the `service_secret.json` file has been [generated](https://developers.google.com/identity/protocols/oauth2/service-account#creatinganaccount) and downloaded. 

## Running
The GoBridge service will run when the docker compose file is fired up. You can view any logs by running `docker logs gobridge`

```
$ python3 GoBridge.py

   _____       ____       _     _            
  / ____|     |  _ \     (_)   | |           
 | |  __  ___ | |_) |_ __ _  __| | __ _  ___ 
 | | |_ |/ _ \|  _ <| '__| |/ _` |/ _` |/ _ \
 | |__| | (_) | |_) | |  | | (_| | (_| |  __/
  \_____|\___/|____/|_|  |_|\__,_|\__, |\___|
                                   __/ |     
                                  |___/

                     SMTP to GMail API Server
                     V0.1

[+] Running GoBridge SMTP server on port  2500
[+] Successfully inserted message for glenn@widgets.com with Id: 186b32c792dcd88e
[+] Successfully inserted message for hazel@widgets.com with Id: 186b32c82342242f
[+] Successfully inserted message for brie@widgets.com with Id: 186b32c8abc5f0b0
[!] An error occurred inserting mail for nosuchuser@widgets.com: invalid_grant: Invalid email or User ID
[!] An error occurred inserting mail for glenn@baddomain.com: invalid_grant: Invalid email or User ID
```
As can be seen in the above output, email addresses not in the scope of the service account will be rejected.


## Modifications

Download this whole repository and amend the .env file to align with your own environment. You should not need to amend much else, however may wish to look at the following line and amend with any other domains you will use for portals:
```
- "traefik.http.routers.gophish-router.rule=Host(`gophish.$DOMAIN`) || Host(`host2.com`)
```

## Docker running

From the root of this directory, run `docker compose up -d`

### References:
https://developers.google.com/gmail/api/reference/rest/v1/users.messages/insert
https://console.cloud.google.com/iam-admin/serviceaccounts
https://developers.google.com/identity/protocols/oauth2/service-account#creatinganaccount
https://developers.google.com/cloud-search/docs/guides/delegation#python
https://stackoverflow.com/questions/42438902/gmail-api-user-impersonation-python
