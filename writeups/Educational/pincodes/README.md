# pincodes
Author: sweeet
## Description
```
Category: Misc/ML

A <redacted company> has recently added a new and hip way of creating a pincode in order to better protect the customer data. This consist of first creating a 5 to 10-digit pincode (it's always 5 numbers, but each number can contain double digits up to and including 19 so a pincode could be "15 12 0 1 19"),
which is then run through an AI model in order to create a second code. During a recent break-in on their servers there was a leaked list of known pincodes, an AI related file, a secret image and one of their server side scripts. 
It's very likely that one of the EPT members have been using the company site in order to store one of the CTF flags. So perhaps you can figure out how to calculate the 2nd pin and get the flag.

`nc {{host}} {{port}}`

```
## Provided challenge files
* [model.h5](model.h5)
* [pincodes.txt](pincodes.txt)
* [potential_solve.py](potential_solve.py)
* [server.py](server.py)
* [confidential.png](confidential.png)
