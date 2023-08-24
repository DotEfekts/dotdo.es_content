# HTB Hardware Challenges - Prison Escape
[Prison Escape](https://app.hackthebox.com/challenges/prison-escape) is a medium difficulty hardware challenge from Hack the Box. While I enjoyed figuring out the packet protocol, the challenge was hampered somewhat by some confusing feedback from the UI where you "send" your tampered packets.
## Initial Information
Prison Escape provides you with two documents to help you in your attempt to disable the prison alarm system: a map of the prison, and a specification document for the "Omega" RF protocol. A quick look at the map shows you the layout of the prison and the alarm system. While some nice flavour, this map is ultimately not important to solving the challenge.
![A part of the specification document](/content/images/htb-challenges/prison-escape/htb-prison-escape-doc.png)

More essential is the Omega spec document. Looking through this we get some important information, such as codes for different commands and the fact that the protocol uses CRC validation for its packets. Helpfully, the document tells you the initial value used for the CRC algorithm.  Okay so that's some information, but not enough to quite understand the whole protocol yet. For that we'll need to intercept some existing packets.

## Packet Interception
It's time to navigate to the interface provided for showing information about your mission, and for sending your tampered packets. On this page there are 4 main elements: your packet sending form, information about the current state of the prison alarm system, a place to intercept packets being sent from the system, and the state of your agent inside the prison.

As we don't know how to send packets just yet, let's intercept some packets for analysis. Click the download capture button, and get a few packets to work with. (There are 5 distinct packets to find, however the filename is randomised so you won't know which of the 5 you'll get.) These packets are downloaded as `.complex` files. If you've done signal analysis before, you might know these files are for holding data about analog signals. If you have `inspectrum`  you can have a quick look at the signal in there, however we're going to need something that can analyse the signal for us as well if we want to get anywhere soon. For this we're going to use [Universal Radio Hacker](https://github.com/jopohl/urh). 

## Packet Analysis
Open up some of the packets you've downloaded in `urh`. The parameters for the signal should be autodetected on import, and you should now be presented with the bits in the packet. You can change this to hex to make it easier to work with.![The signal after importing into urh](/content/images/htb-challenges/prison-escape/htb-prison-escape-urh-signal.png)

You may notice some of these parameters are what the packet sending form in the mission interface asks for. Along with the frequency provided in the document, you now have almost everything you need to start sending tampered packets. We just need to figure out what data to send! Finish importing a few signals into `urh` and then switch to the "Analysis" tab. Switch the view to hex and there we see some patterns emerge.
![Analysis of the protocol in urh](/content/images/htb-challenges/prison-escape/htb-prison-escape-urh-analysis.png)

You can try using "Analyze Protocol" if you like but it's probably not going to give you anything helpful. Let's start by finding some patterns. It looks like bytes 5 to 7 are fixed. Bytes 1-4 and byte 8 seem to correspond to each other.  If we look in the specification document,  the alarms and lasers are referred to as as `An` and `En` respectively, so we can probably say byte 9 designates our device. Byte 11 seems to match our packet identifiers from the document, with the alarms sending broadcast packets, and the lasers looking to be receiving movement instructions. Finally the last 2 bytes are likely to be our CRC, as the initial value for the CRC was 2 bytes wide. Putting this all together in `urh` might look like this:![The protocol after adding highlighting](/content/images/htb-challenges/prison-escape/htb-prison-escape-protocol.png)

The checksum will be wrong for the moment, because we've not yet specified what parameters we should be using for the CRC. Let's try and figure that out now. Calculating a CRC is a fairly standard algorithm, however we need to know 4 things in order to get the correct output: the initial value (which we know is `0x1d0f`), a polynomial, and whether the input and/or output is reversed, and the final XOR value. We currently only know the initial value, however there are a number of standard algorithms so let's do a quick search for `CRC 1d0f`. There seem to be a number of references to `CRC-CCITT`. We can see if this is the algorithm we're searching for using a number of [online calculators](https://crccalc.com/). Copy the hex value of one of the packets (excluding the CRC) and paste it into a CRC calculator for `CRC-16/CCITT`. Make sure your calculator is accepting a hex input and not an ASCII input or you'll receive the wrong result.![The hex data in a CRC calculator](/content/images/htb-challenges/prison-escape/htb-prison-escape-crc.png)

Success! We've got a valid result for one of our packets. We can copy the information from the calculator into `urh` to have it validate the other packets. (By default `urh` will exclude the preamble so just change the start byte to make sure its included.) `urh` should now show the checksum on each packet as valid.

## Prison Break Time?
Now that we seem to have both the protocol and the checksum algorithm figured out we can start to try and free our agent from their cell. Following the information we've gathered, our packet to turn off an alarm should looks like:

| Preamble for alarm packet | Fixed value | Device type | Receiving device | Buffer? | Command | Checksum |
|---------------------------|-------------|-------------|------------------|---------|---------|----------|
| `aaaaaaaa`                  | `697816`      | `21`          | `a1`               | `ff`      | `f1`      | `8E1A`     |

Putting this data into the packet sender, along with the parameters we got from `urh` and the frequency we got from the document, we can hit send and...

Nothing happens. Hmm. So we've missed something here. It's likely to do with that `ff` byte that hasn't changed. We'll need to figure out what that byte is for to complete the challenge.

## The Missing Byte
So given that this byte hasn't changed in any of the packets we've intercepted it can be difficult to determine what it's for. People that work with RF protocols frequently might be rolling their eyes but for me this was fairly new territory. My initial thought was that it was something to do with preventing replay attacks. The byte would have to be changed to some other number determined by an inbuilt algorithm before the packet would be accepted. This is how some car remotes and garage door openers work. So I created a script to cycle through that bit and generate the checksum before sending a `POST` with that info to the `transmit` endpoint on the mission interface.

You can do this yourself if you'd like before we continue. 

Okay so what did we find out. Well if you cycled the byte on an alarm packet you might soon find your interface looks like this:![The mission screen with an alarm disabled](/content/images/htb-challenges/prison-escape/htb-prison-escape-alarm.png)

Initially I was cycling a laser packet, so my interface looked like this:
![The mission screen with the alarms triggered](/content/images/htb-challenges/prison-escape/htb-prison-escape-laser.png)

Now maybe I'm just an idiot, but the way I interpreted this screen was that I had trigged the alarm on the E1 laser. If you, like me, though the alarm had been tripped because a tampered packet had been detected and something still wasn't quite right with the data we're sending, let me save you some time. This screen is showing that the E1 laser has been turned off, however as the document says, any tampering with the laser system results in the alarms going off. A green alarm in this case is a bad thing. What didn't help my confusion was the fact that sending a turn on packet to a laser also resulted in the alarm being triggered.

So if you're looking at that byte in the packet that turned off the alarm, you'll see that it's `a1`. Hmm? `a1`? As in the first alarm? Of course! The document says that the alarms send a broadcast packet every so often. Broadcasts are normally addressed to the highest bit value in many things. Which means byte 9 is the sender, and byte 10 is the intended receiver. The document doesn't mention the lasers _sending_ notice of their movements (or anything other than the packet identifiers for that matter) but we can assume this is also where the move left and move right packets were originating from. Devs keep note, vague documentation is always a nightmare.

With all this information in hand we can now figure out the correct solution is to send a suppression packet to all the alarms first before turning off all three lasers. 
![The almost completed mission screen](/content/images/htb-challenges/prison-escape/htb-prison-escape-complete.png)
