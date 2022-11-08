# Crypto/rsimpla

```
4096 bit keys are just too secure!
```

Downloaded 3 files: requirements.txt, output.txt and chall.py

Found the ciphertext and the the public key in the file output.txt. 

This looked like the RSA-Chiper challenge, so I tried the decoder tool at https://www.dcode.fr/rsa-cipher 

From the `output.txt`:
* Entered `c` value in `Value of the Chiper message (Integer) C=`
* Entered `e` value in `Public Key E`
* Entered `n` value in `Public Key Value (integer) N`

Pushed the button "Decrypt" and voilà.. flag appeared in the Results box.
