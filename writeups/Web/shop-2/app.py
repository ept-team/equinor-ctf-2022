from flask import Flask, request, make_response, redirect, render_template, send_from_directory, session
import random
import string
import os
from flask import Flask, request, send_from_directory, make_response
import hashlib
import random
import string
import requests
from functools import wraps
import time
import re

app = Flask(__name__)

users = {}

items = {
    'gboard': {
        'name': 'Gboard Bar Version',
        'image': '/gboard.jpg',
        'description': 'Simplified and revolusjonary new keyboard Gboard Bar Version!',
        'video': 'https://www.youtube.com/watch?v=9G3DWHf1xX0',
        'price': 60,
        'stars': 4,
        'value': '"the design is very human" - Wise japanese designer'
    },
    'bottle': {
        'name': 'EPT Water Bottle',
        'description': '<p>Join the hydrohomie club with this limited edition EPT Water Bottles!<p/> <i>*Slaps roof of bottle*</i><br>This bottles can fit soo much liquid in them! <br/> <p>Holding their content cold or warm, what ever your prefered brew might be 💦☕️</p> Buy a bottle here within the challenge and then come and claim a physical version at the organizer booth!',
        'image': '/bottle.png',
        'price': 10_000,
        'stars': 5,
        'value': 'The code word is <code>I ❤️ EPT!</code>',
    },
    'flag': {
        'name': 'Flag',
        'description': 'That sweet sweet flag!',
        'image': '/flag.png',
        'price': 10_000,
        'stars': 5,
        'value': open('/flag.txt').read(),
    }
}

def gen_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def has_seen_password(password):
    password = hashlib.sha1(password.encode()).hexdigest()
    res = requests.get(f'https://api.pwnedpasswords.com/range/{password[:5]}')
    for line in res.text.split('\n'):
        suffix, count = line.split(':')
        if suffix == password[5:]:
            return int(count)
    return False


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    data = request.form
    _id = int(data['id']) if 'id' in data else max(*[i for i in users.keys()], 0, 0) + 1
    if _id in users:
        return render_template('register.html', error='Invalid id!'), 400
    if 'username' not in data:
        return render_template('register.html', error='Username is required!'), 400
    _username = data['username']
    if any(_username == user['username'] for user in users.values()):
        return render_template('register.html', error='Username is already taken'), 400
    if not re.fullmatch('[a-zA-Z0-9_]{3,16}', _username):
        return render_template('register.html', error='Invalid username, please try again!'), 400
    if 'password' not in data:
        return render_template('register.html', error='Password is required!'), 400
    _password = data['password']
    if (count := has_seen_password(_password)):
        return render_template('register.html', error=f'Password is too weak! Password has been seen {count} times before!'), 400
    _salt = gen_token()
    users[_id] = {
        'id': _id,
        'username': _username,
        'salt': _salt,
        'password': hashlib.sha512((_salt + _password).encode()).hexdigest(),
        'token': gen_token(),
        'money': 100,
        'inventory': [],
    }
    print(f'[INFO]: User {_username}[{_id}] registered.')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    data = request.form
    if 'username' not in data:
        return render_template('login.html', error='Username is required!'), 400
    _username = data['username']
    for user in users.values():
        if user['username'] == _username:
            if 'password' not in data:
                return render_template('login.html', error='Password is required!'), 400
            _password = data['password']
            if hashlib.sha512((user['salt'] + _password).encode()).hexdigest() == user['password']:
                token = gen_token()
                user['token'] = token
                res = make_response(redirect('/'))
                res.set_cookie('token', token)
                return res
            else:
                return render_template('login.html', error='Invalid username or password'), 401
    return render_template('login.html', error='Unknown user'), 404

@app.get('/logout')
def logout():
    token = request.cookies['token'] if 'token' in request.cookies else 'yikes :/'
    user = [user for user in users.values() if user['token'] == token]
    user = user[0] if len(user) > 0 else None
    if user:
        user['token'] = gen_token()
    res = make_response(redirect('/'))
    res.delete_cookie('token')
    return res

@app.get('/buy/<itemname>')
def buy(itemname):
    token = request.cookies['token'] if 'token' in request.cookies else 'big oof'
    user = [user for user in users.values() if user['token'] == token]
    if len(user) == 0:
        return render_template('index.html', items=items, error='You need to be logged in to buy items!'), 401
    user = user[0]
    if itemname not in items:
        return render_template('index.html', items=items, user=user, error='Item not found'), 404
    item = items[itemname]
    if user['money'] < item['price']:
        return render_template('index.html', items=items, user=user, error='You can not afford that item!'), 402
    user['inventory'].append(itemname)
    print(f'[INFO]: User {user["username"]}[{user["id"]}] bought {item["name"]} for {item["price"]}')
    user['money'] -= item['price']
    print(f'[INFO]: User {user["username"]}[{user["id"]}] new balance: {user["money"]}')
    return redirect('/')


@app.get('/sell/<itemname>')
def sell(itemname):
    token = request.cookies['token'] if 'token' in request.cookies else 'big oof'
    user = [user for user in users.values() if user['token'] == token]
    if len(user) == 0:
        return render_template('index.html', items=items, user=user, error='You need to be logged in to sell items!'), 401
    user = user[0]
    if itemname not in items:
        return render_template('index.html', items=items, user=user, error='Item not found'), 404
    item = items[itemname]
    if itemname not in user['inventory']:
        return render_template('index.html', items=items, user=user, error='You do not own that item!'), 404
    user['inventory'].remove(itemname)
    user['money'] += item['price']
    print(f'[INFO]: User {user["username"]}[{user["id"]}] sold {item["name"]} for {item["price"]}, new balance: {user["money"]}')
    return redirect('/')

@app.get('/item/<itemname>')
def item(itemname):
    token = request.cookies['token'] if 'token' in request.cookies else 'aii...'
    user = [user for user in users.values() if user['token'] == token]
    if len(user) == 0:
        return render_template('index.html', items=items, user=user, error='You need to be logged in to sell items!'), 401
    user = user[0]
    if itemname not in items:
        return render_template('index.html', items=items, user=user, error='Item not found'), 404
    item = items[itemname]
    if itemname not in user['inventory']:
        return render_template('index.html', items=items, user=user, error='You do not own that item!'), 404
    return render_template('item.html', item=item, itemname=itemname, items=items, user=user)


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files(path):
    if path == 'index.html':
        token = request.cookies['token'] if 'token' in request.cookies else 'yikes :/'
        user = [user for user in users.values() if user['token'] == token]
        user = user[0] if len(user) > 0 else None
        return render_template('index.html', items=items, user=user)
    return send_from_directory('static', path)


if __name__ == '__main__':
    import os
    os.system('ls -lAF')
    app.run(host='0.0.0.0', port=8000)