# vegetables
Author: vcpo
## Description
```
Category: misc

Can you help Rick find his pickles? 

`nc {{host}} {{port}}`

```
## Provided challenge files
* [vegetables.tar.gz](vegetables.tar.gz)


---

## Solution
Pickle is a way to serialize an object.

The function that will print the correct flag is in the fruits.py file.

The input from us will be base64 decoded and then unpickled, but the unpickle function has been overloaded to also make sure that the name of the pickled object is 'Rick'.

There is a known issue with pickle that you can also overload the __reduce__() function, and this will be called when you unpickle an object. The __reduce__() function should return 2 arguments where the first will be a function that will be called and the second should be a tuple of arguments to the function. By importing fruits and then providing the address of fruits.Rick, we'll make it call the correct Rick function for our purpose.

The solve.py file will generate such a base64 encoded pickled instance of a Rick class object, and passing this string to the server would make it print out the flag. 