# rip

The source code `rip.c` uses the function *gets()* to get user-input, which is vulnerable to a buffer-overflow attack.

We find the offset for overwriting the RIP-register to be 120 using [find_offset.py](find_offset.py).

We find the address of the assembly *ret*-instruction using ROPgadget (this step can be omitted, but will work with it included as well)
```bash
$ ROPgadget --binary rip --only ret
Gadgets information
============================================================
0x000000000040101a : ret

Unique gadgets found: 1
```

We need the *win()* function's address so we can overwrite the RIP-register with it
```python
 elf.symbols["win"]
```
Sending the crafted payload with `offset + ret + win`overwrites the RIP-register with *win()*'s function address, giving us shell 
