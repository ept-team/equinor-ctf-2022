import json
peda.execute('file ./limbo')
#puts @ main+317
peda.set_breakpoint('*main+369') 
peda.execute('pset option context ""')
output = 'instructions.txt'
peda.execute("run")
i = 0
instructions = {}
libc_base = 0x00007ffff7d91000
libc_offset = 0x28000
libc_size = 0x195000
with open(output, 'w') as f:
    for i in range(3000):
        peda.execute('si')
        rip = peda.getreg('rip')
        print(f' rip is {hex(rip)}')
        instr = peda.current_inst(rip)
        if instr[0] < libc_base+libc_offset or instr[0] > libc_base+libc_offset+libc_size:
            continue
        nextInstr = peda.next_inst(rip, count= 1)
        instrLength = nextInstr[0][0] - instr[0]
        data = peda.dumpmem(rip,rip+instrLength)
        print(f'instruction length is: {instrLength}, data: {data.hex()}')
        jsonInstr = {'address' : hex(instr[0] - libc_base), 'instr' : instr[1], 'data': data.hex() }
        print(i)
        # f.write(f'{hex(instr[0])}: {instr[1]}, data: {data.hex()}\n')
        f.write(json.dumps(jsonInstr) + "\n")
        i+=1



