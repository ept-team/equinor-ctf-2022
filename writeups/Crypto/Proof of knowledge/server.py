#!/usr/bin/env python3
from pydoc import plain
from random import randint
from flask import Flask, render_template, make_response, request, jsonify
from Crypto.Random import get_random_bytes
import sys
import os
import json
from Crypto.Random.random import randrange
from waitress import serve
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from binascii import hexlify, unhexlify
from base64 import b64encode

app = Flask(__name__)
flag = open("flag.txt", "r").read()

KEY            = get_random_bytes(32)
SIGNING_SECRET = get_random_bytes(32)
IV_LENGTH      = 16

burned_challenges = set()

OK = 0
REUSE = 1
BADSIGN = 2
TRYHARDER = 3

def get_sign(message):
    h = MD5.new()
    h.update(SIGNING_SECRET + message)
    return h.hexdigest()

def get_challenge():
    challenge_length = randint(16, 32)
    challenge = get_random_bytes(challenge_length)
    cipher = AES.new(KEY, AES.MODE_CTR)
    ct_bytes = cipher.encrypt(challenge)
    nonce = hexlify(cipher.nonce).decode()
    ct = hexlify(ct_bytes).decode()
    mac = get_sign(challenge)
    result = json.dumps({'nonce':nonce, 'ciphertext':ct, "signature": mac}, indent=4, sort_keys=True)
    return result


def verify_response(ciphertext, nonce, plaintext, sig):
    ciphertext_bytes = unhexlify(ciphertext)
    if ciphertext_bytes in burned_challenges:
        return REUSE, None
    burned_challenges.add(ciphertext_bytes)
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=unhexlify(nonce))
    decrypted_challenge = cipher.decrypt(ciphertext_bytes)
    if get_sign(decrypted_challenge) != sig:
        return BADSIGN, None
    if decrypted_challenge == unhexlify(plaintext):
        return OK, None
    else:
        return TRYHARDER, hexlify(decrypted_challenge).decode("ASCII")

@app.route('/', methods=['GET'])
def index():
    return make_response(render_template('index.html'))

@app.route('/challenge', methods=['POST', 'GET'])
def chall():
    return challenge(randrange(14,20))

@app.route('/challenge', methods=['POST', 'GET'])
def challenge(challenge_length):
    if request.method == 'POST':
        result, solution = None, None
        try:
            ciphertext = request.form["ciphertext"]
            nonce = request.form["nonce"]
            plaintext = request.form["plaintext"]
            sig = request.form["signature"]
            result, solution = verify_response(ciphertext, nonce, plaintext, sig)
        except:
            pass
        if result == REUSE:
            return make_response(render_template('reuse.html'))
        elif result == BADSIGN:
            return make_response(render_template('badsign.html'))
        elif result == TRYHARDER:
            return make_response(render_template('tryharder.html', plaintext=plaintext, solution=solution))
        elif result == OK:
            return make_response(render_template('flag.html', flag=flag))
        else:
            return make_response(render_template('challenge.html', challenge=get_challenge()))
    else:
        return make_response(render_template('challenge.html', challenge=get_challenge()))

if __name__ == '__main__':
    if sys.platform.lower() == "win32": 
        os.system('color')
    serve(app, host="0.0.0.0", port=1234)