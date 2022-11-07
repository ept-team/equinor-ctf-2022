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