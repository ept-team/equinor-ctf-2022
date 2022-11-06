# THE THIEF
Author: nordbo
## Description
```
We detected that someone got in to our network and stole our vaction photos! Luckily for you, we pcap everything!
Take a look and see if you can find our pictures.

```
## Provided challenge files
* [thethief.pcap](thethief.pcap)

## Solution

When we open the provided pcap challenge file in Wireshark, we quickly notice
some abnormal DNS traffic.

The DNS requests query name have a structure like this:

```
   <random chars>-.<random chars>-.<random chars>-.<random chars>-.<filename>
```

This looks like a DNS exfiltration technique, where each <random chars> section
is a base64 encoded piece of data, and the final field referencing the target
filename.

We can use `dpkt` ([link](https://pypi.org/project/dpkt/)) library to parse the
pcap file in python to reassemble the base64 encoded sections. We also notice
that there are some `*` characters in the encoding. We'll just replace those
with `+` before we decode the data.

```python
import dpkt
import socket
import base64

def main():
    files = {}

    f = open("thethief.pcap", "rb")
    for ts, buf in dpkt.pcap.Reader(f):
        eth = dpkt.ethernet.Ethernet(buf)

        # we only care about IP packets
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue

        ip = eth.data

        # we only care about UDP packets
        if ip.p != dpkt.ip.IP_PROTO_UDP:
            continue

        udp = ip.udp

        # we only care about UDP packets going to 54.75.80.140
        if ip.dst != socket.inet_aton("54.75.80.140"):
            continue

        # decode udp data as DNS
        dns = dpkt.dns.DNS(udp.data)

        # get the DNS query name
        qdname = dns.qd[0].name

        # tokenize on "-."
        toks = qdname.split("-.")

        # filename is the last token
        fname = toks[-1]

        # reassemble chunks based on filename
        if not fname in files:
            files[fname] = ""

        for chunk in toks[:-1]:
            files[fname] += chunk.replace("*", "+")

    # reassembling done, base64 decode and write to disk
    for fname in files:
        data = base64.b64decode(files[fname])
        with open(fname, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    main()
```

Once we look at the output, we notice that the files are compressed with `gzip`.
Use the `gunzip` tool to decompress and then find the flag in one of the images.

