#!/bin/env python3
import requests
import json
import hashlib
import string
import random
import pickle
from termcolor2 import colored

GREEN = '\033[32m'
YELLOW = '\033[93m'
RED = '\033[31m'
BLACK = '\033[30m'

# OPTIMIZE
def findguess(hashes, its, size):
    def compare(guess, hash):
        out = 0
        for i in range(len(guess)):
            if hash[i] == guess[i]:
                n = 0
            elif str.find(hash, guess[i]) != -1: # should be i not 1
                n = 2
            else:
                n = 1
            out += n
            out <<= 2 # edit this if add back middle
        return out

    def find_num_uniq(hashes, guess):
        uniq = set()
        for cur_hash in hashes:
            uniq.add(compare(guess, cur_hash))
        return len(uniq)

    best = 0
    bestguess = ""
    letters = string.ascii_lowercase
    for _ in range(its):
        guess = ( ''.join(random.choice(letters) for _ in range(32)) )
        guess_md5 = hashlib.md5(bytes(guess, 'utf-8')).hexdigest()[:size]
        score = find_num_uniq(hashes, guess_md5)
        if score > best:
            best = score
            bestguess = guess
    # print(f"Best guess: {bestguess}, uniq: {best}")
    return bestguess


# MAIN

base = "http://io2.ept.gg:32195"

guess_url = base + "/api/guess"

def read_rockyou():
    # f = open("rockyou.txt", "rb")
    # txt = f.read()
    # lines = txt.split(b"\n")
    # hashes = []

    # for line in lines:
        # h = hashlib.md5(line)
        # hashes.append(h.hexdigest())
        # if len(hashes) % 1000000 == 0:
            # print(len(hashes))
    
    # p = open("pickle", "wb")
    # pickle.dump((lines, hashes), p)

    # return lines, hashes
    p = open("pickle", "rb")
    print("Load...")
    return pickle.load(p)

lines, hashes = read_rockyou()
orig_hashes = hashes

def get_token():
    r = requests.get(base + "/api/session")
    return json.loads(r.text)["token"]

def guess_req(token, something):
    r = requests.post(guess_url, json={
        "token":token,
        "password":something
        })
    j = json.loads(r.text)
    return j

def guess(token, something):
    j = guess_req(token, something)
    try:
        hints = j["hash"]
    except:
        print("Failed:", j)
        exit(1)

    chars = [v["char"] for v in hints]
    cols = [v["hint"] for v in hints]

    return (chars, cols)

def set_print(s):
    l = [v for v in s]
    l.sort()
    print(l)

def remove_impossible(remaining_hashes, yellows, size):
    new = []

    for h in remaining_hashes:
        good = True
        for key, value in yellows.items():
            if h[:size].count(key) != value:
                good = False
                break
        if good:
            new.append(h)

    return new


# find the password
def interact(token, remaining_tries):
    yellows = {}

    remaining_hashes = hashes

    for itn in range(99):
        print(f"{remaining_tries} tries left")
        if itn == 0:
            rnd = "bdpbyjtjabkxabpcdrkjeyasuwicjyoy"
        else:
            print("Finding guess...")
            if remaining_tries >= len(remaining_hashes):
                print(colored("Bruting last tries", "red"))
                return remaining_hashes
            rnd = findguess(remaining_hashes[:50000], 100, len(chars))
        print(f"> {rnd}")
        chars, cols = guess(token, rnd)
        remaining_tries -= 1

        possible = [ set([c for c in "0123456789abcdef"]) for _ in range(len(chars)) ]

        print("< ", end="")
        for char, col in zip(chars, cols):
            if col == "green" or col == "yellow":
                print(colored(char, col), end="")
            else:
                print(colored(char, "red"), end="")
        print("")

        for i in range(len(chars)):
            if cols[i] == "green": # this is correct
                possible[i] = { chars[i] }
            elif cols[i] == "yellow": # this is not correct
                possible[i].discard(chars[i])
            elif cols[i] == "none": # this is never correct

                ys = 0
                for j in range(len(chars)):
                    if (cols[j] == "yellow" or cols[j] == "green") and chars[j] == chars[i]:
                        ys += 1

                if chars[i] in yellows:
                    assert(yellows[chars[i]] == ys)

                yellows[chars[i]] = ys

        # remove based on yellow count
        print("YELLOW before", len(remaining_hashes))
        remaining_hashes = remove_impossible(remaining_hashes, yellows, len(possible))
        print("YELLOW after", len(remaining_hashes))

        if len(remaining_hashes) == 1: # shouldnt be required anymore
            return [remaining_hashes[0]]

        print("NORMAL Finding matching hashes...")
        ps = find_hash(possible, remaining_hashes)
        if len(ps) == 1:
            print(f"finished at iteration {itn+1}")
            return [ps[0]]
        else:
            print(f"Found {len(ps)}, down from {len(remaining_hashes)}")
            remaining_hashes = ps

        print("")

    print("failed")
    exit(1)


def find_hash(possible, hashlist):
    def fil(maybe):
        for char, pos in zip(maybe, possible):
            if not char in pos:
                return False
        return True
    
    good = filter(fil, hashlist)
    good = [g for g in good]

    return good

def password_from_hash(target):
    for h, p in zip(hashes, lines):
        if h == target:
            return p.decode('utf-8')
    print("NO PASSWORD!")
    exit(1)

def password_from_known(known_chars):
    def filt(maybe):
        for a, b in zip(maybe, known_chars):
            if a != b and b != " ":
                return False
        return True

    good_hashes = filter(filt, hashes)

    for has in good_hashes:
        for k, v in zip(hashes, lines):
            if k != has:
                continue

            txt = v.decode('utf-8')
            return txt

token = get_token()
max_tries = 0
cur_lev = 1
while True:
    hs = interact(token, max_tries)

    if len(hs) > 1:
        print(colored(f"Bruting", "red"))

    for h in hs:
        pwd = password_from_hash(h)
        print(colored(f"Submitting {pwd}...", "green"))
        r = guess_req(token, pwd)
        if cur_lev > 10:
             print(r)
        try:
            new_token = r["token"]
        except:
            print("missing token!")
            print(r)
            exit(1)
        if new_token != token:
            print(colored("Token changed", "magenta"))
            exit(1)

        new_level = r["level"]
        if new_level != cur_lev:
            print(colored(f"\n== LEVEL {new_level} ==", "magenta"))
            cur_lev = new_level
            max_tries = r["max_attempts"]
            break
