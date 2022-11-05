import os
from flask import Flask, render_template, session, url_for, request, abort, redirect, make_response
import os
from string import ascii_lowercase
from random import seed, randbytes, choice

def generate_random_key():
    key = randbytes(1)
    key += choice(ascii_lowercase).encode("ascii")
    return key
flag = open("flag.txt", "r").read()
app = Flask(__name__)
seed(flag)
app.secret_key = generate_random_key()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.clear()
        name = request.form['name']
        if name == "admin":
            abort(403)
        session['name'] = name
        return redirect(url_for('index'))
    else:
        name = session.get('name')
        if name and name == "admin":
            return make_response(render_template('index.html', name=name, flag=flag))
        elif name:
            return make_response(render_template('index.html', name=name, flag="*"*12))
        else:
            return make_response(render_template('register.html'))

@app.route('/unregister', methods=['GET'])
def unregister():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
   app.run(debug=True)