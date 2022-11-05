from flask import Flask, request, make_response, redirect, render_template, send_from_directory, session
import random
import string
import os

app = Flask('EPT-Shop')
confdir = os.path.join('/app/', app.name, '/etc/')
if not os.path.exists(confdir):
    os.makedirs(confdir)
    random_process_context = random.choices(string.ascii_letters + string.digits, k=16)
    open(os.path.join(confdir, 'rpc'), 'w').write(random_process_context)

app.secret_key = open(os.path.join(confdir, 'rpc')).read()

items = {
    'meme': {
        'name': 'Meme',
        'image': '/meme.png',
        'description': 'Your very own meme!',
        'price': 60,
        'stars': 3,
        'value': 'Firefox-chan FWT!'
    },
    'sticker': {
        'name': 'EPT Stickers',
        'image': '/sticker.png',
        'description': '<p>Hang them on the wall. Hang them on your laptop. Hang them on your bag. These stickers will make any item they stick to look +10% cooler 😎</p> Buy a sticker here within the challenge and then come and claim a physical version at the organizer booth!',
        'price': 10_000,
        'stars': 5,
        'value': 'The code word is <code>I ❤️ EPT!</code>'
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


@app.get('/buy/<item>')
def buy(item):
    if item not in items:
        return render_template('item.html', money=session['money'], error='Sawy, i downt know abwout dwat itweam!'), 404
    item = items[item]
    if session['money'] < item['price']:
        return render_template('item.html', money=session['money'], error='Sawy, u cawn not afwawd dwat itweam!'), 402
    session['money'] -= item['price']
    return render_template('item.html', money=session['money'], item=item)


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files(path):
    if 'money' not in session:
        session['money'] = 100
    if path == 'index.html':
        return render_template('index.html', items=items, money=session['money'])
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
