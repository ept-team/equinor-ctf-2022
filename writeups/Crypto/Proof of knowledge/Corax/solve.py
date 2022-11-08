import requests # this allows us to make web requests
import re # this allows us to filter strings with regex

# because the SSL certificate on ept.gg was poorly configured :P
import warnings
warnings.filterwarnings("ignore")

# I'm addicted to regex now
pre_element = r"<pre>[\x00-\xff]+</pre>" # fetches everything inside the pre-tags of an HTML document
hex_strings = r"[0-9a-fA-F]{16,64}" # fetches hex strings between 8 and 32 bytes
flag_string = r"EPT{.*}" # fetches flag

# defines a bitwise-xor function for two byte strings
xor = lambda a,b:bytes(i^j for i,j in zip(a,b))

# set up a session for the challenge
url = "https://proof-of-knowledge.io.ept.gg/challenge"
session = requests.Session()

# function to scrape hex strings from the page
def scrape_values(page_content):
	# extract the pre-element from the HTML page
	pre_content = re.findall(pre_element,page_content)[0]
	# extract the hex strings from the pre element
	hex_values = re.findall(hex_strings, pre_content)
	# pack this data neatly in a dictionary
	# if we get three hex strings, the page contains ciphertext
	if len(hex_values) == 3:
		values = {
			name:bytes.fromhex(hexstr) \
			for hexstr, name in \
			zip(hex_values,["ciphertext","nonce","signature"])
			}
	# if it contains two, it contains plaintext
	elif len(hex_values) == 2:
		values = {
			"plaintext":bytes.fromhex(hex_values[1])
		}
	else:
		return None
	# return the dictionary
	return values

# we start by generating two encrypted messages
req1 = session.get(url, verify=False).content.decode()
encrypted1 = scrape_values(req1)
req2 = requests.get(url, verify=False).content.decode()
encrypted2 = scrape_values(req2)

# ensure the first ciphertext is longer than the 2nd by swapping the two if it isn't
if len(encrypted1["ciphertext"]) < len(encrypted2["ciphertext"]):
	encrypted1, encrypted2 = encrypted2, encrypted1

# fetch the real plaintexts of the encrypted messages
# by submitting the ciphertext, nonce and signature
# with a fake plaintext
plaintexts = []
for ciphertext in [encrypted1,encrypted2]:
	body = {
		key:value.hex() for key,value\
		in ciphertext.items()
	}
	body.update({"plaintext":ciphertext["ciphertext"].hex(),"challenge":""})
	req = session.post(url, data = body, verify=False).content.decode()
	plaintexts.append(scrape_values(req))


# now that we've fetched all the parts, time for the attack
# we start with recovering the cipherstream for our first plaintext
# since CTR-mode effectively functions as a steam-cipher,
# we may perform a bitwise-XOR on the plaintext and ciphertext
# to recover a cipherstream
plaintext1 = plaintexts[0]["plaintext"]
ciphertext1 = encrypted1["ciphertext"]
cipherstream1 = xor(plaintext1, ciphertext1)

plaintext2 = plaintexts[1]["plaintext"]
ciphertext2 = encrypted2["ciphertext"]
cipherstream2 = xor(plaintext2, ciphertext2)

# we forge a new ciphertext by encrypting
# the 2nd plaintext with the 1st cipherstream
forged_ciphertext = xor(plaintext2, cipherstream1)

# combining everything into a forged message
forged_proof = {
	"ciphertext":forged_ciphertext.hex(),
	"nonce":encrypted1["nonce"].hex(),
	"signature":encrypted2["signature"].hex(),
	"plaintext":plaintext2.hex(),
	"challenge":""
}

# sending the forged message to the server and retrieving the flag
flag_page = session.post(url, data = forged_proof, verify=False).content.decode()
flag = re.findall(flag_string, flag_page)[0]

# printing the flag
print(flag)
