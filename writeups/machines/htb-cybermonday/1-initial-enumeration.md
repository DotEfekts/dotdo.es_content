The [Cybermonday](https://app.hackthebox.com/machines/557) box was my first hard Hack the Box challenge and phew, it was a lot. You should have a good grasp of application logic, JSON and Web APIs, serialisation methods, and Docker. All of these and more come into play on this box.
# HTB Cybermonday - Initial Enumeration

[**Initial Enumeration**](/writeups/machines/htb-cybermonday/1-initial-enumeration)
[Webhook API Admin Access](/writeups/machines/htb-cybermonday/2-webhook-api-admin)
[Obtaining More Info](/writeups/machines/htb-cybermonday/3-obtaining-more-info)
[Gaining a Foothold](/writeups/machines/htb-cybermonday/4-gaining-a-foothold)
[Where to Now?](/writeups/machines/htb-cybermonday/5-where-to-now)
[Reading the Source](/writeups/machines/htb-cybermonday/6-reading-the-source)
[Composing Root Access](/writeups/machines/htb-cybermonday/7-composing-root-access)

First we run `nmap` to see what services are available on the box.
```shell
$ nmap -sV --open -oG initial_scan <machine ip>

Host: <machine ip> ()
Ports: 
22/open/tcp//ssh//OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)/, 
80/open/tcp//http//nginx 1.25.1/
```

SSH and a HTTP server. We don't have an credentials yet so we won't bother attempting to connect to the SSH server. Instead let's look at what's available on the HTTP server.

Trying to connect to the server we're immediately redirected to `http://cybermonday.htb/`. Looks like we'll need to add the domain to our `/etc/hosts` file to continue. Once we've added that and navigated to the web page again we see an online shopping website, with various products and a landing page.

![The Cybermonday homepage](/writeups/machines/htb-cybermonday/images/htb-cybermonday-home.png)

Enumerating through the pages doesn't seem to show anything interesting, so lets sign up for an account and see what else we can find. Once logged in we see a basic account page. The items in the list are just for show but there is a link to a profile page.

![The Cybermonday profile page](/writeups/machines/htb-cybermonday/images/htb-cybermonday-profile.png)

Opening this lets us edit different aspects of our account. Let's try some SQL injection to see if basic measures have at least been taken. No luck, we just have a funny name now. Instead lets see what happens if we try to set our username to admin.

![The Laravel debug page](/writeups/machines/htb-cybermonday/images/htb-cybermonday-laravel.png)

Ah ha, a debug page. Here we can see the version of PHP and Laravel that are being used, as well as some details about the update function we've just used. If we scroll down we can see some user info. 

![The user details on the debug page](/writeups/machines/htb-cybermonday/images/htb-cybermonday-user.png)

That `isAdmin` field looks interesting. If we look back at the update function we can see it just takes the data we've provided and directly updates the database with the information. If we use our browsers developer tools to update the form and include `isAdmin` (SQL databases generally accept booleans as a 0 or a 1, so use a number input rather than a checkbox):

![The dashboard link is now shown](/writeups/machines/htb-cybermonday/images/htb-cybermonday-dashboard.png)

Success, we've now had a new link added we can navigate to. If we look through we can see a few different pages. The dashboard seems to just be some placeholder graphs. On the products page we can add new products to the list on the products page. Looking at the images there however, they're sent through as data URLs so probably not useful for file injection.

![The Cybermonday upload screen](/writeups/machines/htb-cybermonday/images/htb-cybermonday-upload.png)

On the last page in changelog we can see an interesting link. A link to a webhook API in the testing stages.

Next: [Webhook API Admin Access](/writeups/machines/htb-cybermonday/2-webhook-api-admin)