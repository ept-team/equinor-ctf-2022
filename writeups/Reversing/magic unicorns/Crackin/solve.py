from z3 import *
from pwn import *

passwd = IntVector('x', 7*7)
user_hash = Int('y')
s = Solver()

#  function A
for counter in range(7):
  tmp = f's.add('
  for i in range(7):
    tmp += f'passwd[{counter * 7 + i}] + '
  tmp = tmp[:-3] + f' == user_hash)'
  eval(tmp)

# function B
for counter in range(7):
  tmp = f's.add('
  for i in range(7):
    tmp += f'passwd[{i * 7 + counter}] + '
  tmp = tmp[:-3] + f' == user_hash)'
  eval(tmp)

# function C
counter = 6
tmp = f's.add('
for i in range(7):
  tmp += f'passwd[{i * 7 + counter}] + '
  counter -= 1
tmp = tmp[:-3] + f' == user_hash)'
eval(tmp)

# function D
counter = 0
tmp = f's.add('
for i in range(7):
  tmp += f'passwd[{i * 7 + counter}] + '
  counter += 1
tmp = tmp[:-3] + f' == user_hash)'
eval(tmp)

# function E
for counter in range(7):
  for i in range(7):
    if i != counter:
      s.add(passwd[counter * 7 + counter] != passwd[i*7 + counter])
  j = counter + 1
  if j < 7:
    s.add(passwd[counter * 7 + counter] != passwd[counter*7 + j])

# Give user_hash of `admin`
# But migh works with any user_hash
s.add(user_hash == 0x5ee6)

# Let z3 do his magic
s.check()

# Get the results
result = s.model()

p = process('./magic')
# p = remote("io.ept.gg",30050)

# Adapt the user_name if you changed the user_hash in z3
p.sendline(b'admin')


# Recover the z3 variables
# This part is a bit dirty, there might have a better way to get them
result = re.findall(b'x__(\d+) = (-?\d+)', str(result).encode())
result = sorted(result, key=lambda x: int(x[0].decode()))

password = [(x[1].decode()) for x in result]
print(password)

for i in password:
  p.sendline(i)

p.interactive()