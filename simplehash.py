'''
this is not a security way to handle password, it is just obsciruty, i got the mac as a key, maybe it helps
keeping the password/string key unique for only that PC, so if the code is stolen it may prove a little harder to decrypt
by Felipe Ferreira 02/2018
'''

import base64
from uuid import getnode as get_mac

def mencode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def mdecode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


password="soeuseiessaparada"

chave = str(get_mac())
print(chave)

hpass=mencode(chave, password)
print(hpass)

cpass=mdecode(chave, hpass)
print(cpass)
