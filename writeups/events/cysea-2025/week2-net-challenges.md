# Week 2 - Network Challenges
In week 2, a bonus set of challenges were released for participants to attempt. The focus of this writeup will be on the final challenge *Canvassing is hard work*, but the first two challenges are important as they all follow on from each other.
## A telling tale 
For this challenge, we're given some details about a "fortune teller" that left a business card for one of the characters in the CTF story, and asked if we can find out what the fortune teller had to say. To start the challenge, a hostname is provided, but no further details. There's no HTTP server at the host, so the next step is to run a scan with `nmap`.
```
dot@stuff:~$ sudo nmap -sS office.centrist.freedonia.vote
Starting Nmap 7.95 ( https://nmap.org ) at 2025-07-25 01:49 UTC
Nmap scan report for office.centrist.freedonia.vote (192.168.1.1)
Host is up (0.017s latency).
rDNS record for 192.168.1.1: ec2-54-153-192-232.ap-southeast-2.compute.amazonaws.com
Not shown: 995 closed tcp ports (reset)
PORT   STATE    SERVICE
7/tcp  open     echo
9/tcp  open     discard
17/tcp open     qotd
19/tcp open     chargen
22/tcp filtered ssh
```
We have some context from the CTF Discord that any `filtered` ports are not part of the challenge and can be ignored. Here we have 4 open ports along with a guess from `nmap` as to what may be available on them. The services normally on these ports are all older debug protocols. The `echo` protocol sends back whatever data is sent to it, the `discard` protocol returns nothing at all, and the `chargen` service sends a predefined repeating set of characters. Finally, we have the `qotd` protocol, or "Quote of the Day". This is a service that will return daily quote when connected to, and is the service most likely to provide us with further info. 
```
dot@stuff:~$ nc office.centrist.freedonia.vote 17        

If you want your luck to hold, make sure you have the winning numbers.
Got off at the wrong stop? Maybe you should try a different form of transport.
cysea{y0uv3_n3773d_a_f0r7un3}
```
Connecting to the service doesn't provide anything initially, but if we hit enter a few times we receive back a random quote each time. There are three that are cycled between: A quote about having the winning numbers, a quote about trying different forms of transport, and finally the flag for the first challenge. We can take the flag and then move on to challenge number 2.
## Lottery ticket
In this challenge we're asked to retrieve a copy of the CTF characters lottery ticket from the office server, likely the numbers that were referred to by the "winning numbers" quote from the first challenge. Since we don't have the numbers yet, lets focus on the other quote from the previous challenge, that being "a different form of transport". This is likely a hint to try a different form of network transport, i.e. UDP.  Trying to connect to the quote service via UDP instead of TCP doesn't seem to work, but what about the other services? The `chargen` service just gives us a bunch of characters each time we hit enter.
```
dot@stuff:~$ nc office.centrist.freedonia.vote 17 -u

dot@stuff:~$ nc office.centrist.freedonia.vote 19 -u

!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefgh
"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghi
#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghij
$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijk
%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijkl
&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklm
'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghi
```
The `discard` service doesn't seem to work either. Connecting to the `echo` service however, looks to do the trick.
```
dot@stuff:~$ nc office.centrist.freedonia.vote 9 -u 

dot@stuff:~$ nc office.centrist.freedonia.vote 7 -u

cysea{fr33d0n14_numb3r5_202,97,131,1033}
```
We now have both the flag and the lottery numbers, and can move on to the final challenge.
## Canvassing is hard work
In the final challenge we have very little to go off save a bit of a longer description that gives us a few hints where to look next. With both the description of the challenge, and the previous hint from the quote of the day service, it's fairly clear the "lottery numbers" in the previous flag will play a role in completing this challenge. We also have some interesting wording in the final paragraph, this being that we should be "urgent, without being pushy". Searching for some variations of "urgent network attribute", we can find that TCP packets have an option to set an `URG` or urgent flag, and from there you may also find the existence of the `PSH` or push flag, or "urgent" and "pushy".  Initially I thought the other reference to "something quote worthy" meant sending the lotto numbers to the quote service using the urgent flag but my tests with that didn't seem to go anywhere. Eventually I had a thought while re-reading the challenge description; it mentions that the story's character "spends three or four hours every day visiting the residents ... in their homes". Another term for canvassing in a political context is "door knocking", which sounds awfully similar to "port knocking". So what if we take our lottery numbers and start knocking? We're going to use `scapy` so we can fully control the packets we send to each port, setting the `URG` flag (without the `PSH` flag) for our "knocks".
```python
from scapy.all import *
import socket
import time

target = "office.centrist.freedonia.vote"
lottery_ports = [202, 97, 131, 1033]
target_ip = socket.gethostbyname(target)

def knock_ports():
    for port in lottery_ports:
        pkt = IP(dst=target_ip)/TCP(dport=port, flags="SU")
        send(pkt, verbose=False)
        time.sleep(1)

if __name__ == "__main__":
    knock_ports()
```
After we run this script, we should use `nmap` again to see if any new services are available to us.
```
dot@stuff:~$ sudo nmap -sS office.centrist.freedonia.vote
Starting Nmap 7.95 ( https://nmap.org ) at 2025-07-25 09:51 AWST
Nmap scan report for office.centrist.freedonia.vote (192.168.1.1)
Host is up (0.051s latency).
rDNS record for 192.168.1.1: ec2-54-153-192-232.ap-southeast-2.compute.amazonaws.com
Not shown: 994 closed tcp ports (reset)
PORT   STATE    SERVICE
7/tcp  open     echo
9/tcp  open     discard
17/tcp open     qotd
19/tcp open     chargen
21/tcp open     ftp
22/tcp filtered ssh
```
Success! We now have an FTP service available to us to connect to. Lets use a command line FTP client to connect using the anonymous user.
```
dot@stuff:~$ ftp office.centrist.freedonia.vote
Connected to office.centrist.freedonia.vote.
220 pyftpdlib 1.5.9 ready.
Name (office.centrist.freedonia.vote:root): anonymous
331 Username ok, send password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering extended passive mode (|||50083|).
125 Data connection already open. Transfer starting.
-rw-r--r--   1 nobody   nogroup        31 Jul 10 09:36 flag.txt
226 Transfer complete.
ftp> 
```
As we can see, there is a `flag.txt` file available for us to download! Let's grab it and check the flag.
```
ftp> get flag.txt
local: flag.txt remote: flag.txt
229 Entering extended passive mode (|||50062|).
125 Data connection already open. Transfer starting.
100% |*********************************************************************************************************************************************************|    31      540.59 KiB/s    00:00 ETA
226 Transfer complete.
31 bytes received in 00:00 (132.19 KiB/s)
ftp> exit
221 Goodbye.
dot@stuff:~$ cat flag.txt 
This flag is a little bit meta
```
Oh, okay not quite that easy then. Telling us the flag is meta probably implies that we need to look at the metadata of the file, but the metadata downloaded from the FTP server is minimal, so we need to check if there are any FTP commands that offer any further metadata. In the command line FTP client we can use the `quote` command to send a raw FTP message to the server. Hmm, `quote`. We still have that "something quote worthy" hint that hasn't been applicable so far, perhaps this is what it's referring to. Let's send a `HELP` message to see what commands are available on the server.
```
ftp> quote HELP
214-The following commands are recognized:
 ABOR   ALLO   APPE   CDUP   CWD    DELE   EPRT   EPSV  
 FEAT   HELP   LIST   MDTM   MFMT   MKD    MLSD   MLST  
 MODE   NLST   NOOP   OPTS   PASS   PASV   PORT   PWD   
 QUIT   REIN   REST   RETR   RMD    RNFR   RNTO   SITE  
 SIZE   STAT   STOR   STOU   STRU   SYST   TYPE   USER  
 XATR   XCUP   XCWD   XMKD   XPWD   XRMD  
214 Help command successful.
```
We can lookup each of these commands online to get some info or just use the `HELP X` command to get info on what each command does.
```
ftp> quote HELP ABOR
214 Syntax: ABOR (abort transfer).
ftp> quote HELP APPE
214 Syntax: APPE <SP> file-name (append data to file).
```
As we look at the `HELP` info for each command, we eventually find the description for the `XATR` command.
```
ftp> quote HELP XATR
214 Syntax: XATR <SP> file-name (Get xattrs of file).
```
Aha, this looks promising. `xattrs`, or "Extended file attributes" are extra information about a file that you can set. They're not standard file system attributes, and aren't normally transferred when downloading via FTP. If you're familiar with FTP commands, or lookup each command, you'll find that `XATR` is not standard in FTP servers and is likely a custom command, almost certainly what we're looking for. Let's run the command on the `flag.txt` file and see what happens.
```
ftp> quote XATR flag.txt
200 xattr fetched {'user.flag': b'cysea{fl4g_r3d4ct3d_s0rry}'}.
```
Success! We've found our flag and completed the challenges.