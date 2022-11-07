# Haxxor

### Preliminaries
We have a webservice where we are invited to log in to get a fake flag. A look at `app.py` reveals that `haxxor` gets us 
to the second page, with a `dict` being passed between the pages in pickled form, and used to render the fake flag.

The fake flag is rendered through the `haxxor()` method, which in turn uses its own `xor()` to XOR the fake flag with
the given key, initially `haxxor`.

As `xor()` returns the length of the shortest string, we only get the first 6 bytes of the fake flag going through the 
first page. To get any further, we need to modify the pickle blob, and from here on we work directly on `/flag`.

Pickling and encoding a dict where the key us much longer, e.g. 
`{'haxxor': 'haxxorhaxxorhaxxorhaxxorhaxxorhaxxorhaxxorhaxxorhaxxorhaxxorhaxxor'}` gets us the full fake flag, but this 
is only a clue: `EPT{Did you really think you could do without RCE? :(}` so we obviously need to dig deeper.

### In a pickle
Pickle is a library for serialising and deserialising Python objects (including functions), and is fairly comprehensive 
and powerful. When deserialising, code is sent through a state machine, and it is possible to create objects and execute
functions that are available in the surrounding scope. 

Pickle streams are sequences of opcodes with or without arguments, operating on a stack. If we could send arbitrary 
pickle code and have it executed, this would be a walk in the park. However, there is a gatekeeper block in the way:
```python
allowedOperation = "haxxor"

...

for p in pickletools.genops(name):
    if(p[1]==None or isinstance(p[1],int)):
        continue
    for op in str(p[1]).lower():
        if(op not in allowedOperation):
            return jsonify({'Error':'NO HACKING!!!'})
```
Pickletools is a useful tool for making and analysing pickle streams, and this loop goes through all the opcode 
arguments to look for HACKING. On its face, this code appears to block any string argument that is not `haxxor`. 
But since the argument characters are turned to lowercase, and also only have to _appear_ in `allowedOperation`, we can 
use any character in `HAXORhaxor` in any order.

### XORing for fun and profit
To execute code using pickle, we need to push the module and name of an existing function on to the stack, use the 
`STACK_GLOBAL` opcode to load the function, push any arguments on the stack and then gathering them into a tuple, and
finally load the `REDUCE` opcode. All well and good, except that any module and function names we define have to pass
through the gatekeeper. So we are pretty much limited to the `haxxor` module, with its `xor()` function. Which isn't too
bad, since we can use the `xor()` function to create new characters from gatekeeper-compliant inputs. Sadly, there 
really aren't too many characters we can create simply by XORing the `HAXORhaxor` characters.

Looking at the `xor()` function, we can see that it stringifies both arguments before XORing their component characters.
Which means that the arguments need not be strings at all, so long as they can be coerced into such. And since the 
gatekeeper lets integer opcode arguments pass through without scrutiny, we can now add `0123456789` to our alphabet.
There are some limitations: we can't have very long words (only up to 4 byte integers can be defined numerically), and
leading `0` digits get lost in the process. 

Using `xor()` and our expanded alphabet, we can now make most characters, and adding a second `xor()` step expands 
this to the entire lower 128 ascii table. But there are still limitations: input arguments to the function must be 
either all `HAXORhaxor` or all integer. Due to the way XOR works and the structure of the ascii table, this means that
we cannot make strings including both characters from the alphabet columns and from the numeric/special 
character column in the same operation. 

Fortunately, `_` is on the alphabet side, so we can make `__add__`. Combined with loading `getattr()` from `builtins` 
we can invoke the string concatenation function to put together any string we like.

### Getting the flag
At this point there are several options to get to the flag itself. We can see that there is a `flag.txt` containing it, 
and also an executable `flag` that simply reads and prints `flag.txt`. It seems a shame not to use the executable when 
it's there, so we put together the opcodes to run `os.popen('/flag').read()`.

### Escape somehow
Once we have the flag, we need to exfiltrate. Again there are several options, but `app.py` comes with an unused 
function:
```python
@app.errorhandler(403)
def custom403(error):
    return jsonify({'Error': error.description})
```
This error handler will take over execution and return any second argument we put into `flask.abort(403, message)`, 
which is a clean and handy way to get the booty.

### Putting it all together
It may be possible to create a Python object to do all this and then get pickle to make a haxxor-compliant bytestream, 
but it seems unlikely. So we build the stream ourselves, using whatever documentation we can scrounge together. 
The `pickletools` library was very useful for analysing streams and understanding what was going on when the streams 
were loaded.

`solve.py` defines the functions and constants needed for the requisite opcodes, and then puts them all together for a 
nice 'name' to send to the server, yielding the flag `EPT{Ar3_Y0U_4_h4xx0r???}`

