# Encrypt all the files

```
Someone encrypted our system files by accident. We suspect there was a flag in there...
```

We're given two files for this challenge, `encryptor.py` and `cef3c355f173f8b2.zip`. The former file is a python script that encrypts all files in the input directory and stores the encrypted versions of these files with the MD5-sums of the plaintext content as the file name. The encryption is done through 2048-bit repeated XOR using a stream generated using AES-CFB on a random byte stream.

In order to decrypt the files, we need to recover the repeated cipherstream used to encrypt the files. There are two ways to do this, one by doing some light OSINT and the other through a more thorough cryptanaltic process.

## Recovering the cipherstream - the OSINT way

The easier of the two ways to recover the cipherstream is by simply googing the MD5-sums and find plaintext data. This is ultimately the method I ended up going for as it was the path of least resistence.

The file named `20c5329d7fde522338f037a7fe8a84eb` was the biggest clocking in at roughly 11 megs, so this is the one I went for. Googing it shows results like WinSCP. I found the file `WinSCP-5.21.5-Setup.exe` hosted at the website file horse: https://www.filehorse.com/download-winscp/download/

checking the MD5 sum to ensure I haven't accidentally downloaded an NSO-group-developed malware trojan or Mongolian dating simulator:

```
$ md5sum WinSCP-5.21.5-Setup.exe
20c5329d7fde522338f037a7fe8a84eb  WinSCP-5.21.5-Setup.exe
```

Fits the bill!

Alright, now to recovering the XOR-key, I wrote the following solve script:

```py
import re
from os import listdir
from itertools import cycle

with open('WinSCP-5.21.5-Setup.exe','rb') as f:
	plaintext = f.read(2048)

with open('20c5329d7fde522338f037a7fe8a84eb','rb') as f:
	ciphertext = f.read(2048)

xor = lambda a,b:bytes(i^j for i,j in zip(a,b))

xor_key = xor(plaintext,ciphertext)


md5string = r'^[0-9a-f]{32}$'
for filename in listdir():
	if not re.match(md5string, filename) is None:
		with open(filename,'rb') as f:
			contents = f.read()
		with open(f'{filename}.dec','wb') as f:
			f.write(xor(contents,xor_key))
```

This script will recover the cipherstream, then decrypt all files whose file name is an hex-encoded md5 hash and store the plaintext in a file with a `.dec` extention. Now let's see what type of files we're dealing with:

```
$ file *.dec
6cdc78e2f348f2f63fc20f7b014bb4c6.dec: LZMA compressed data, streamed
20c5329d7fde522338f037a7fe8a84eb.dec: PE32 executable (GUI) Intel 80386, for MS Windows
7233110888fcead21adb89b25c4edd73.dec: ASCII text, with CRLF line terminators
e32f72e15f78347c51c4ca1b2847f667.dec: PE32+ executable (GUI) x86-64, for MS Windows
```

Scroll down to Part 2 to see the continuation of this challenge...


## Recovering the cipherstream - the cryptanalytic way

Alternatively we could recover the cipherstream using cryptanalysis. Assuming the larger files are of file types with large sections of repeating null-bytes, like for example executables or file systems, we may sample a few 2048-byte chunks of these files and run a majority function on all the bytes across the chunks to recover the cipher stream:

```py
import re
from os import listdir
from itertools import cycle

chunks = []

md5string = r'^[0-9a-f]{32}$'
for filename in listdir():
	if re.match(md5string, filename) is None:
		continue
	with open(filename,'rb') as f:
		while len(chunks)<200:
			ciphertext = f.read(2048)
			if len(ciphertext) == 2048:
				chunks.append(ciphertext)
			else:
				break

def majority(s):
	return max(set(s), key = s.count)

xor = lambda a,b:bytes(i^j for i,j in zip(a,b))

xor_key = bytes(majority([j[i] for j in chunks]) for i in range(2048))

md5string = r'^[0-9a-f]{32}$'
for filename in listdir():
	if not re.match(md5string, filename) is None:
		with open(filename,'rb') as f:
			contents = f.read()
		with open(f'{filename}.dec','wb') as f:
			f.write(xor(contents,cycle(xor_key)))
```

This will decrypt the files, as we may verify by taking the md5-sum:

```
$ md5sum *.dec

6cdc78e2f348f2f63fc20f7b014bb4c6  6cdc78e2f348f2f63fc20f7b014bb4c6.dec
20c5329d7fde522338f037a7fe8a84eb  20c5329d7fde522338f037a7fe8a84eb.dec
7233110888fcead21adb89b25c4edd73  7233110888fcead21adb89b25c4edd73.dec
e32f72e15f78347c51c4ca1b2847f667  e32f72e15f78347c51c4ca1b2847f667.dec

$ file *.dec
6cdc78e2f348f2f63fc20f7b014bb4c6.dec: LZMA compressed data, streamed
20c5329d7fde522338f037a7fe8a84eb.dec: PE32 executable (GUI) Intel 80386, for MS Windows
7233110888fcead21adb89b25c4edd73.dec: ASCII text, with CRLF line terminators
e32f72e15f78347c51c4ca1b2847f667.dec: PE32+ executable (GUI) x86-64, for MS Windows
```

Yup, looks about right! Now we may continue with part 2 of the challenge...

## Part 2 of the challenge: Shakespear 

Okay, we're getting somewhere. Looks like we got some ASCII text and an LZMA-zipped archive. Let's take a look at the ASCII text first:

```
wget -UseBasicParsing -Uri "https://raw.githubusercontent.com/brunoklein99/deep-learning-notes/master/shakespeare.txt" -OutFile text.txt
```

Hmmm, it's downloading a text file. The text file in question is a compilation of the sonnets by William Shakespeare.

Let's take a look at the LZMA archive:

```
$ cp 6cdc78e2f348f2f63fc20f7b014bb4c6.dec something.lzma
$ lzma --decompress something.lzma
$ file something
something: ASCII text
```

This file seems to be the Sonnets just like `text.txt`, but a few characters are different. I wrote another quick python-script to compare the files:

```py
with open('text.txt','r') as f:
	shakespear = f.read()
with open('something','r') as f:
	not_shakespear = f.read()
for i,j in zip(shakespear, not_shakespear):
	if i != j:
		print(j,end="")
```

Running this script prints out `TheFlagIsHiddenSomewhereHereOkayHereYouGoEPT{21af48eb6f04db3731b86a2ec10f19e7}IThinkItShouldBeEasyEnoughToGet`, and there's our flag!


