# Proof of knowledge

The challenge is to input the four values `ciphertext`, `nonce`, `plaintext` and `signature`, where the values have the following relations:
```
ciphertext = AES.encrypt(plaintext, mode=AES.CTR, nonce=nonce)
signature = md5(secret_string + plaintext)
```

We are provided with three values: the nonce, the ciphertext, and the signature. So we were not provided with the plaintext (our task is to find the plaintext).
If we give the three values and a random plaintext, then we server will return the proper plaintext. However, we cannot use this as every ciphertext can only be submitted once.

The way we solved this was by using two tuples of (`ciphertext_i`, `nonce_i`, `plaintext_i`, `signature_i`) for `i=1,2` to generate a new valid tuple that has never been submitted.
The solution is in the way that `AES.CTR` works. Every `nonce` gives a stream of bytes that the `plaintext` is xored with in order to get the `ciphertext`. We can use this to get a new ciphertext.

```
new_ciphertext = ciphertext_2 xor plaintext_2 xor plaintext_1
```

Then we have `new_ciphertext = AES.encrypt(plaintext_1, mode=AES.CTR, nonce=nonce_2)`. Thus (`new_ciphertext`, `nonce_2`, `plaintext_1`, `signature_1`) is a new valid tuple. We submitted this and got the flag. We don't have a solve script as we used cyberchef to do this.
