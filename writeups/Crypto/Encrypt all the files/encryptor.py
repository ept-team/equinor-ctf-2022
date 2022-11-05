import os,sys
import shutil
from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from binascii import hexlify
from itertools import cycle

if len(sys.argv) < 2:
    print(f'Input directory to encrypt, e.g.: "{sys.argv[0]} C:\documents"')
    exit(1)
directory = sys.argv[1]

key = get_random_bytes(16)
cipher = AES.new(key, AES.MODE_CFB)
xor_key = cipher.encrypt(get_random_bytes(2048))

working_folder = hexlify(get_random_bytes(8)).decode()
try:
    os.makedirs(working_folder)
except:
    pass

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        file = open(f, "rb").read()
        h = MD5.new()
        h.update(file)
        ciphertext = bytes(c^k for c,k in zip(file, cycle(xor_key)))
        with open(os.path.join(working_folder, f"{h.hexdigest()}"), "wb") as encrypted_file:
            encrypted_file.write(ciphertext)

shutil.make_archive(working_folder, 'zip', working_folder)
shutil.rmtree(working_folder)