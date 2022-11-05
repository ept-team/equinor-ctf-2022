from Crypto.Util.number import bytes_to_long, getPrime
from sympy import nextprime

a_prime = getPrime(2048)
b_prime = getPrime(2048)
p = nextprime(a_prime)
q = nextprime(b_prime)
n = p * q
e = 3
flag = open("flag.txt", "r").read().encode("utf-8")
assert flag.startswith(b"EPT{")
assert flag.endswith(b"}")
assert len(flag) == 51
c = pow(bytes_to_long(flag), e, n)

with open('output.txt', 'w') as f:
    f.write(f"e: {e}\n")
    f.write(f"n: {n}\n")
    f.write(f"c: {c}\n")