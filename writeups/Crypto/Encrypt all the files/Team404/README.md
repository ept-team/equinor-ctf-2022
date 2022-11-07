## Solution

You are provided a zip archive of encrypted files and the python script that was
used to create the archive.

The challenge is to decrypt the encrypted files and find the flag.

When we analyze the `encryptor.py` script, we see that the encrypted target
filename is the result of the MD5 hexdigest of the original file content.

We also see that the `xor_key` used to encrypt the file content is 2048 bytes.

If we recover the `xor_key`, we can simply run the XOR operation with the
`xor_key` to recover the file contents.

The trick here is that the MD5 hashes (ie the filename of the encrypted files)
are well-known hashes, and the original files can be obtained online. E.g the
MD5 hash `e32f72e15f78347c51c4ca1b2847f667` corresponds to `putty.exe`, version
`0.77` [link](https://the.earth.li/~sgtatham/putty/0.77/w64/putty.exe).

If we XOR the encrypted contents of `putty.exe` (ie the file named
`e32f72e15f78347c51c4ca1b2847f667`) with the original file, we will recover the `xor_key`.

```python
# encrypted file
enc = open("e32f72e15f78347c51c4ca1b2847f667", "rb").read(2048)

# known plain file
pln = open("putty.exe", "rb").read(2048)

key = bytearray()
for idx in range(len(enc)):
    key += (enc[idx] ^ pln[idx]).to_bytes(1, 'little')

# write the xor key to file
with open("xor_key.bin", "wb") as f:
    f.write(key)
```

With the `xor_key` recovered, we can decrypt all of the files.

When we decrypt the file `6cdc78e2f348f2f63fc20f7b014bb4c6` we identify this as
an LZMA compressed file. We can decompress this using `lzmadec`.

Once it's decompressed, we find the text "THE SONNETS" by Willian Shakespeare.

When we decrypt the file `7233110888fcead21adb89b25c4edd73` we find a URL that
is referencing the same text. When we download this text and compares it do the
one we decrypted, we see that they are slightly different.

To find the differences, use the diff tool in CyberChef and select "Show
subtraction" to get an easy to read view of the differences. The resulting
difference output will reveal the flag.
