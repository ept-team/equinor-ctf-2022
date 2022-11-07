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