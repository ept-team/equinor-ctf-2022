## A solution to Flask Session

This task requires us to get the admin session-token. 🚩

We can logg into the app with any username except  **"admin"**, and get a session-token of our own.

One keynote in this task is that Flask session-tokens are not randomly generated. If the input parameters are the same, the session-token will always be the same. 

At startuptime the flask app sets a random seed that we must find to if we want to forge the admin session-token. `app.secret_key = generate_random_key()`. 


```py
def generate_random_key():
    key = randbytes(1)
    key += choice(ascii_lowercase).encode("ascii")
    return key

```

The function to generate a random key returns a 2 byte long bytestring. That's a short key... why not brute force it.

I used a prpgram called flask-unsign, and used my own session-token and matched it with all possible bytestrings. After a few seconds I got the `secret_key`

```sh
flask-unsign --unsign --cookie eyJuYW1lIjoiYWRtaW4gIn0.Y2VvNQ.M1L7uzTGPsRD0n-J-0kGhIvKoZA -w "./all_possible_bytestrings.txt" --no-literal-eval
```

`app.secret_key = f"\x13x"`.

Then we ran the flask app locally (commented out the admin check) and did a curl to get the admin session token.

`curl --dump-header header.txt http://127.0.0.1:5000 -d "name=admin"`


Finally, we logged in to the webapp with admin credentials and got the flag. 🚩