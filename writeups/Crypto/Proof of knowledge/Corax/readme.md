
# 🔥Proof of knowledge🔥

```
You need to prove knowledge of the secret to get the flag

Site: proof-of-knowledge.io.ept.gg
```

We're provieded two files `server.py` and `Dockerfile`, these are provided so that we can read through and understand the server-side code as well as test our solution locally.

The file `server.py` shows us what happens on the site, we see that there is a symmetric signature scheme based on a hash-based message authentication code. I struggled initially with this challenge, because I focused on the poorly implemented HMAC which was vulnerable to an length extention attack, however the overall design of the challenge made such an attack infeasable due to the relatively short ciphertexts.

Every time we load the site, we're given somether ciphertext, a nonce, and a signature. If we're able to provide a piece of ciphertext, a nonce, a signature and the correct plaintext belonging to the ciphertext, we will be given the flag. Providing validly encrypted and signed ciphertext but invalid plaintext will give us the valid plaintext.

The encryption scheme used is AES256 CTR-mode encryption. This encryption works by encrypting the sequentially nonce appended with a counter and performing a bitwise-XOR with the plaintext to obtain the ciphertext. In practice this means CTR-mode functions as a stream cipher, which opens for bit-flipping attacks. CTR-mode encryption/decryption visualized:

![CTR-mode decryption](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/CTR_decryption_2.svg/601px-CTR_decryption_2.svg.png)

By reading the server code given, we can make some key insights that will help us solve the challenge:

- we can recover the plaintext of any message by submitting the ciphertext, nonce and signature given
- we can recover the cipherstream used by bitwise XOR-ing a plaintext with its ciphertext
- signatures are generated only from plaintexts and are entirely independent from the nonce and ciphertext
- we can arbitrarily encrypt valid messages by bitwise XOR-ing it with a recovered cipher stream
- the only constraint on submitting ciphertexts is that we cannot submit the same ciphertext twice
- we can recover the plaintext message belonging to a known signature by submitting the ciphertext, nonce and signature given on the start page

Thus, we can take a known plaintext-signature pair and encrypt it with a recovered cipherstream, we will know the nonce that generated said cipherstream, thus by submitting this nonce along with the plaintext-signature pair and the plaintext bitwise XOR-ed with the cipherstream, we can generate a forged ciphertext that will decrypt to this plaintext which we have the signature for. Doing so will give us the flag.

Here is a thoroughly commented [solve script](solve.py) that fully automates this attack and prints the flag to the terminal, use it to gain a better understanding of this attack.