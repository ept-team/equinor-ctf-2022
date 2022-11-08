from hashlib import md5
from requests import session
from collections import defaultdict
import pickle, random
from hashes import SINGLE, ALPHA

## Uncomment first time to create a hash lookup
# lookup = {}
# for word in open("rockyou.txt","rb").read().splitlines():
    # h = md5(word).hexdigest()
    # lookup[h] = word
# pickle.dump(lookup, open("lookup.bin","wb"))
lookup = pickle.load(open("lookup.bin","rb"))


while True:
    s = session()
    data = s.get("http://io7.ept.gg:32958/api/session").json()

    TOKEN = data["token"]
    LEVEL = data["level"]
    MAX_ATTEMPTS = data["max_attempts"]
    ATTEMPTS_REMAINING = data["max_attempts"]
    LENGTH = data["length"]

    running = True
    while running:
        WON = False
        known = [None]*LENGTH
        wrong = [None]*LENGTH
        counts = {}
        mincounts = defaultdict(int)

        if MAX_ATTEMPTS > 10:
            segment = SINGLE + ALPHA
        else:
            segment = ALPHA

        for l in segment[:MAX_ATTEMPTS-1]:
            res = s.post("http://io7.ept.gg:32958/api/guess", json={"password":l, "token":TOKEN}).json()
            ATTEMPTS_REMAINING -= 1
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

            if None not in known: # We can break early :)
                break

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
                print(word)
                res = s.post("http://io7.ept.gg:32958/api/guess", json={"password":word.decode(), "token":TOKEN}).json()
                ATTEMPTS_REMAINING -= 1
                print(res["level"], res["flag"], res["max_attempts"])

                if "EPT" in res["flag"]:
                    print(res["flag"])
                    input("????")

                if res["level"] > LEVEL:
                    LEVEL = res["level"]
                    LENGTH = res["length"]
                    MAX_ATTEMPTS = res["max_attempts"]
                    break

                elif ATTEMPTS_REMAINING == 0:
                    print("Failed :(")
                    running = False
                    break
        else:
            assert False
