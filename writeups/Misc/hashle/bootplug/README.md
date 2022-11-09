# Hashle writeup

### Challenge description

In this challenge, we're presented with a website and JSON-API that plays wordle using the well-known `rockyou.txt` as a wordlist. The twist is that both the password and our input is hashed with MD5, and the clues (green, yellow or black markings) are given for the hashes. There's also multiple levels with varying difficulty levels.

Difficulty is implemented by truncating the hashes *before* clues are evaluated, together with a varying amount of guesses. For the first few levels, we get the full 32 hex-nibbles of the hash, but the maximum amount of guesses go down with 1 per level. After level 5, the hash is truncated down more and more every level, down to only the 5 first nibbles for the final levels. Guesses do increase again at this point. There is also a hidden timeout in the challenge, probably due to server-side cleanup happening, which means you can't wait too long between every action.

### Strategy

There's multiple ways to go about solving this, but since we went for speed, and didn't know the amount of levels or difficulty when starting, the optimal one wasn't chosen from the get-go.

The most efficient way to solve the challenges, is to come up with an initial hash that has a balanced amount of each nibble, and then prune the list of password candidates based on the response. Observing the remaining candidates, find an input that is able to divide that the candidates the best way. With this, each question is dynamically chosen based on the current information. This does not require that much clever programming, but is quite slow and requires a small amount of brute-forcing.

Another way to go about the challenge, is to pre-pick a few good hash inputs that have a lot of variety. They should not have any nibbles in the same position across guesses, and generally contain all the possible hex-bytes in varying amounts. This is what we chose to do.

With this, we send `max_attempts - 1` hashes each round for the initial rounds, and assume we are able to uniquely identify a password for the last attempt.

### Implementation

Given the responses from our custom hash inputs, we have to make use of all of the information in a response. We made 4 observations from each response:

- Green positions are easy. The password hash *must* match the nibble in this position.

- Yellow and black means the opposite. It can't be equal to the nibble in this positon.

- The presence of a black clue means we have saturated the count of a given hex byte. Now we know exactly how many of that byte is present.

- Yellow clues (without black) give us a lower bound for the count of a given hex byte.

Implementing all of these rules can be done like this

```python
for l in hashes[:MAX_ATTEMPTS-1]:
    res = sess.post("http://io7.ept.gg:32958/api/guess", json={"password":l, "token":token}).json()
    for i,el in enumerate(res["hash"]):
        if el["char"] != "none":
            X = sum(1 for ell in res["hash"] if ell["char"] == el["char"] and ell["hint"]!="none")
            if X > 0:
                mincounts[el["char"]] = max(mincounts[el["char"]], X)
        if el["hint"] == "green":
            known[i] = el["char"]
        elif el["hint"] == "yellow":
            wrong[i] = el["char"]
        elif el["hint"] == "none":
            count = sum(1 for ell in res["hash"] if ell["char"] == el["char"] and ell["hint"]!="none")
            counts[el["char"]] = count
            wrong[i] = el["char"]
```

Iterating over all the passwords is slow, so we made a lookup, pickled it, and loaded/iterated over that. Python was more than fast enough to find candidates, but took up a lot of RAM. Loading the lookup pickle was slow, so the program was created so it could run in an infinite loop once started - to avoid extra loading times. `pypy` made things slightly faster, which made it easier to beat the sporadic timeouts.

```python
lookup = {}
for word in open("rockyou.txt","rb").read().splitlines():
    h = md5(word).hexdigest()
    lookup[h] = word
pickle.dump(lookup, open("lookup.bin","wb"))


...

for h,word in lookup.items():
    h = h[:LENGTH]
    good = True

    for i,e in enumerate(h):
        if known[i] and known[i]!=e:
            good = False
            break

    for i,e in enumerate(h):
        if wrong[i] and wrong[i]==e:
            good = False
            break

    for char,count in mincounts.items():
        if h.count(char) < count:
            good = False
            break

    for char,count in counts.items():
        if h.count(char) != count:
            good = False
            break
    if good:
        res = s.post("http://io7.ept.gg:32958/api/guess", json={"password":word.decode(), "token":token}).json()
        ...
```

Using all our guesses except 1 worked fine until we had only the first 5-6 nibbles of the hash. By then, there were multiple passwords matching the prefix. The amount of guesses increased dramatically at the same time, so we found a lot of inputs that hashed to "000000...", "111111..." etc. Guessing some of these gave us 100% green within a few guesses, and we could then break out early and start guessing multiple passwords until the `level` field in the response increased.



After running a few instances of the program, and with some luck, we finally get the flag and first blood for the challenge



`EPT{1_5we4r_i7_w4s_n0t_ju5t_4_f4d}`




