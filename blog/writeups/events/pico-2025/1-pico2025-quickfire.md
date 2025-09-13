I'm back to participating in CTFs with [CASSA's RedRoom](https://cassa.au/redroom-flag-goes-here/) and starting things off with the picoCTF 2025 event. It was my first time in a timed event and it was fun relearning some of the things I learnt from Hack the Box and learning some new concepts as well.
# picoCTF 2025 - Quick Fire Round

[**Quick Fire Round**](1-pico2025-quickfire)

To start off I'll quickly list the easier challenges and how to solve them. If you're here looking for hints rather than answers turn away now!
### FANTASY CTF
A quick little choose your own adventure story to let you know the rules for the CTF. We can just progress through the story to get the flag.
### Ph4nt0m 1ntrud3r
We're given a PCAP file containing some TCP packets with various different pieces of data. Open it up in Wireshark and sort by Time, the latest packets contain Base64 encoded pieces of the flag. Decode them and assemble the flag.
### Cookie Monster Secret Recipe
Open the link to the challenge, and we'll be presented with a login page. We can use any details to login, and it will result in an access denied screen with a hint to check your cookies. Open up the browser dev tools and we find a new cookie with a Base64 encoded value. Decode the string and we'll have the flag.
### head-dump
Start the instance and open up the website. We can click around to the different sections but the important part is the `#API Documentation` link in the post about Node.js. Open the Swagger UI and scroll to the bottom where the `/heapdump` endpoint is. Use the inbuilt API explorer or your favourite REST client to query the endpoint and download the `.heapsnapshot` file, then search the file with `grep` or your text editor to find the `picoCTF` flag.
### Flag Hunters
This challenge provides the Python source to analyse in order to exploit the input and obtain the flag. The goal is to trigger the `RETURN [0-9]+` pattern in order to skip the "song" back to the secret intro section with the flag. `re.match` matches the entire line so we can't just put the `RETURN 0` command in on its own as the input will have `Crowd: `  added to the start. If you look at the loop for printing the song, we can see that each line in the song has `.split(';')` applied to it, and each split is then matched. In which case we can just do `;RETURN 0` instead, and after the program runs through the song, we'll have the flag.
### PIE TIME
This one involves just a little math. We're given a binary and its source, along with a connect command for inputing our answer. If we look in the source file, we can see our goal is to trigger the `win` function to have the program print the flag. To do this, the program tell us the address of the main function, then asks us for an address to jump to. We can find out that address by running `objdump -d vuln` on the binary file we downloaded. With this we can see that the `win` function is at `12a7` and the main function is at `133d`. If you've already used the connect command you might see the address the program actually gives is very different to the one from `objdump`. That's because the `objdump` addresses are given starting from `0` whereas in memory the starting address will be different. The functions will still have the same relative addresses though so we can use a hex calculator to find the difference between the `main` and `win` functions. Plugging this in we get a difference of `96`. So now we connect to the program, subtract `96` from the address provided, and enter this in the `0xADDRESS` format. If you've done this all correctly it will print the flag.
### RED

### Rust fixme 1
This one has a Rust program to fix and run. This one is particularly easy, just follow the comments in the `main.rs` file then build the program using the Cargo manifest. Run the resulting program and it will give you the flag.
### Rust fixme 2
The next one is more or less the same as the first one. You need to edit the `party_foul` variable and the `borrowed_string` parameter to be mutable. Build it with Cargo again and run the program to get the flag.
### Rust fixme 3
Last one. The comments in this teach you about unsafe operations in Rust. Uncomment the unsafe block, build the program, and run it to get the flag.
### 