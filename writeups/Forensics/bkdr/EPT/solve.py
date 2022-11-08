import time
import frida
import json
import msf
import struct
from msf import *



enc_cipher_hashcodes = [] #cipher objects with Cipher.ENCRYPT_MODE will be stored here
dec_cipher_hashcodes = [] #cipher objects with Cipher.ENCRYPT_MODE will be stored here


#Code to dissect MSF packets is mostly ripped from https://raw.githubusercontent.com/REW-sploit/REW-sploit/main/modules/meterpreter_reverse_tcp.py with some modifications
#to parse the data from our hooked javax.crypto.Cipher rather than from a PCAP.
msf_tlvid = {getattr(msf, item): item
             for item in dir(msf) if item.startswith("TLV_TYPE_")}
msf_cmdid = {getattr(msf, item): item
             for item in dir(msf) if item.startswith("COMMAND_ID_")}

def extract_tlv(pkt):
    tlv = []

    offset = 0

    while offset < len(pkt) - 1:

        tlv_value = None

        # Get length and type
        tlv_len, tlv_type = struct.unpack(
            ">II", pkt[offset:offset + HEADER_SIZE])

        # Extract values
        # String
        if tlv_type & TLV_META_TYPE_STRING == TLV_META_TYPE_STRING:
            tlv_value = pkt[offset + HEADER_SIZE:offset + tlv_len]
        # UINT
        elif tlv_type & TLV_META_TYPE_UINT == TLV_META_TYPE_UINT:
            tlv_value = struct.unpack(
                ">I", pkt[offset + HEADER_SIZE:offset + HEADER_SIZE + 4])[0]
        # QWORD
        elif tlv_type & TLV_META_TYPE_QWORD == TLV_META_TYPE_QWORD:
            # FIXME
            tlv_value = struct.unpack(
                ">Q", pkt[offset + HEADER_SIZE:offset + HEADER_SIZE + 8])[0]
        # Bool
        elif tlv_type & TLV_META_TYPE_BOOL == TLV_META_TYPE_BOOL:
            # FIXME
            tlv_value = -1
        else:
            # Raw
            tlv_value = pkt[offset + HEADER_SIZE:offset + tlv_len]

        tlv.append({'type': tlv_type, 'len': tlv_len, 'value': tlv_value})
        offset += tlv_len

    return tlv

def print_tlv(tlv):    
    for t in tlv:
        
        #Filtering out some noise from irrelevant types
        if(t['type'] in (0x10002,0x20036,0x2001B,0x20900,0x20BC0,0x20032,0x20019)):
            continue
        print('')
        try:
            print('Type:   %s (0x%X)' %
                         (msf_tlvid[t['type']], t['type']))
        except KeyError:
            print('Type:   %s (0x%X)' % ('TLV_TYPE_UNK', t['type']))
        print('Length: %d' % t['len'])
        if t['type'] == TLV_TYPE_COMMAND_ID:
            try:
                print('Value:  %s (0x%X)' %
                             (msf_cmdid[t['value']], t['value']))
            except KeyError:
                print('Value:  %s (0x%X)' %
                             ('COMMAND_ID_UNK', t['value']))
        #Skip printing raw screenshot data
        elif t['type'] != 0x40BBA:
            print('Value:  %s' % t['value'])

def my_message_handler(message, payload):
    #mainly printing the data sent from the js code, and managing the cipher objects according to their operation mode
    if message["type"] == "send":
        my_json = json.loads(message["payload"])
        if my_json["my_type"] == "hashcode_enc":
            enc_cipher_hashcodes.append(my_json["hashcode"])
        elif my_json["my_type"] == "hashcode_dec":
            dec_cipher_hashcodes.append(my_json["hashcode"])
        #We are excluding outgoing commands and data as we are only interested in incoming requests
        #elif my_json["my_type"] == "before_doFinal" and my_json["hashcode"] in enc_cipher_hashcodes:
            #if the cipher object has Cipher.MODE_ENCRYPT as the operation mode, the data before doFinal will be printed
            #and the data returned (ciphertext) will be ignored
            #print_tlv(extract_tlv(payload))
        elif my_json["my_type"] == "after_doFinal" and my_json["hashcode"] in dec_cipher_hashcodes:
            #print("Decrypted TLV data :", payload)
            print_tlv(extract_tlv(payload))

    else:
        print(message)
        print('*' * 16)
        print(payload)


device = frida.get_usb_device()
pid = device.spawn(["de.spiritcroc.riotx"])
device.resume(pid)
time.sleep(1)  
session = device.attach(pid)

with open("script.js") as f:
    script = session.create_script(f.read())
script.on("message", my_message_handler)  
script.load()

input()