# rsaimpla

```
4096 bit keys are just too secure!
```

We're given three files, `chall.py`, `output.txt` and `requirements.txt`.

Look at `chall.py`, we see that the flag has been encrypted with RSA-4096, and the ciphertext along with the public key is saved in `output.txt`. The modulus of the public key is securely generated, however they've chosen to use `e = 3` as the public exponent. They have also not padded the message before encryption. This creates a series of problems, but one of them is that if the message is too short, it will not be affected by the modulus and encryption will just be standard exponentiation by 3.

There are two solutions to this challenge, the most straightforward one is to simply take the cubic root of the ciphertext to recover the plaintext:

```py
from Crypto.Util.number import long_to_bytes as l2b
from gmpy2 import iroot
import re

# read file content
with open('output.txt','r') as f:
	output = f.read()

# extract variales from file content
e,n,ct = tuple(int(i) for i in re.findall(r'\d+',output))

# take the cube root of the ciphertext, decode message as bytes
flag = l2b(iroot(ct, e)[0]).decode()

# print flag :)
print(flag)
```

Running this script prints the flag.