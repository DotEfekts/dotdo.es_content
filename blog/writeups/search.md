## [HTB Season II - Cybermonday](1-initial-enumeration)
A hard machine from the season two releases from HTB, with many steps needed to even obtain a shell. As the first hard box I've done I struggled in a few places, but having had experience with Docker, I found obtaining root relatively simple. #htb #machine #web #redis #docker
## [HTB Hardware Challenge - Prison Escape](htb-prison-escape)
A hardware challenge from HTB. It involves interpreting RF packet data to decipher the protocol being used. I thought this challenge was okay but made harder by an unclear UI and contradictory responses. #htb #hardware #challenge #network
## [The Australian Cyber Security Games 2025](cysea-2025)
A set of writeups from the Australian Cyber Security Games 2025, a CTF run over 5 weeks, open to cybersecurity students in Australia. #ctf
## [Network Challenges](week2-net-challenges)
In week 2, a bonus set of challenges were released for participants to attempt. The focus of this writeup will be on the final challenge *Canvassing is hard work*, but the first two challenges are important as they all follow on from each other. #ctf #challenge #network #ftp
## [Following Protocol](following-protocol)
For this challenge, we're provided with the source code to a voting web app and asked to find out who the user "wbc" has voted for. The source contains a Docker compose file and several different apps, tied together with a front end Node app that we're given the URL for. #ctf #challenge #web #redis #nginx
## [The voting logs ain't making sense](voting-logs)
Most people probably managed to solve this one, and probably solved it using the intended method, however I ended up solving this one before doing the intended method for *I can be anyone!* and then used the same method to solve both challenges. This is how I did *I can be anyone!* the hard way. #ctf #challenge #web #jwt
## [Who checks the integrity of the integrity checks?](integrity-checks)
In this challenge, we're told that there was a mismatch in votes and asked if it's possible to tamper with the printed receipts. We're given the source code for a printer server, but no address for where its located.  #ctf #challenge #web #network
## [Log of Doom](log-of-doom)
This challenge mentions an experimental feature in the logging portion of the mobile backend. Looking at the code we can see the `/vote-logs` endpoint has a section for retrieving votes from a `file` source, along with a note that it's experimental. This section, specifically the `read_vote_file` function, will be our target for this challenge. #ctf #challenge #network #lfi
## [This Things Rigged and Digital Ballots](this-things-rigged)
In this challenge, we're provided with the URL to a "tallyroom" website, with live updates of a vote count in a fictional election. The description of the challenge mentions that the new system is "decentralized and distributed" but asks where to documentation for the system is. #ctf #challenge #osint #web #lfi
## [AI/LLM Challenges](tallyroom-llm)
These challenges ask you to try and obtain secrets the LLM has been told to protect, with the *Oh, Llamma!* flag being easier to obtain than the *Machine Coercion Protection* flag. We can actually obtain both flags with a single prompt, using the "translate the above" and "write a poem" tricks. #ctf #challenge #ai #llm #lfi
