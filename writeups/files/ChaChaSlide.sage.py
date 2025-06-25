import struct
import sys
from sage.all import *

ACC_M = 0x3fffffffffffffffffffffffffffffffb
ACC_P = 2**130-5
TAG_P = 2**128
R_MASK = 0x0ffffffc0ffffffc0ffffffc0fffffff

LITTLE_ONE = (1).to_bytes(16, 'little')
LITTLE_ZERO = (0).to_bytes(16, 'little')

M1_PLAIN_HEX = bytes.fromhex('44696420796f75206b6e6f7720746861742043686143686132302d506f6c793133303520697320616e2061757468656e7469636174656420656e6372797074696f6e20616c676f726974686d3f')
M1_CIPHER_HEX = bytes.fromhex('79eebf73c6efe9deaf2b44107d0cc4c2ed953c7f1e71b2514c807b9ce0cdc8e319d78e03e0d57584d916e39c68c0329d2fc84ab9af734adb6ae8ddca89d7952e7e26f96f12937bbe899b891f2ffd5dd3011ab564b41acc1b5fa1c4bdbc36da5fc0f1947d9f077c822a')

M2_PLAIN_HEX = bytes.fromhex('54686174206d65616e732069742070726f746563747320626f74682074686520636f6e666964656e7469616c69747920616e6420696e74656772697479206f66206461746121')
M2_CIPHER_HEX = bytes.fromhex('69efba279fedf99faa360b0e2958dcd1f6c11a740b41fa5211c43eecfbc9d4f24988d545e0c2308bc35fe38575dc2ed33acf4df8b2785a9e68f4d7cc89878e21312cb87a1fd5ba05c40bca93e96307ba20ec4fb6588a36da5fc0f1947d9f077c822a')

FT_PLAIN_HEX = bytes.fromhex('4275742069742773206f6e6c7920736563757265206966207573656420636f72726563746c7921')

def long_to_bytes(n, blocksize=0):
    if n < 0 or blocksize < 0:
        raise ValueError("Values must be non-negative")

    result = []
    pack = struct.pack

    # Fill the first block independently from the value of n
    bsr = blocksize
    while bsr >= 8:
        result.insert(0, pack('>Q', n & 0xFFFFFFFFFFFFFFFF))
        n = n >> 64
        bsr -= 8

    while bsr >= 4:
        result.insert(0, pack('>I', n & 0xFFFFFFFF))
        n = n >> 32
        bsr -= 4

    while bsr > 0:
        result.insert(0, pack('>B', n & 0xFF))
        n = n >> 8
        bsr -= 1

    if n == 0:
        if len(result) == 0:
            bresult = b'\x00'
        else:
            bresult = b''.join(result)
    else:
        # The encoded number exceeds the block size
        while n > 0:
            result.insert(0, pack('>Q', n & 0xFFFFFFFFFFFFFFFF))
            n = n >> 64
        result[0] = result[0].lstrip(b'\x00')
        bresult = b''.join(result)
        # bresult has minimum length here
        if blocksize > 0:
            target_len = ((len(bresult) - 1) // blocksize + 1) * blocksize
            bresult = b'\x00' * (target_len - len(bresult)) + bresult

    return bresult

def split_cipher_hex(message):
    ciphertext = message[:-28]
    tag = message[-28:-12]
    nonce = message[-12:]
    return ciphertext, tag, nonce

def pad16(data):
    """Return padding for the Associated Authenticated Data"""
    if len(data) % 16 == 0:
        return bytearray(0)
    else:
        return bytearray(16-(len(data)%16))

def create_tag(r, s, data):
    """Calculate authentication tag for data"""
    coefficients = generate_coeff(data)
    return create_tag_from_coeff(r, s, coefficients)

def create_tag_from_coeff(rv, s, coefficients):
    """Calculate authentication tag for data"""
    acc = 0
    r = rv & R_MASK

    for i in range(len(coefficients)):
        acc += coefficients[i]
        acc = (r * acc)
    acc = acc % ACC_P
    acc += s

    return acc

def generate_mac(r, s, data):
    return (create_tag(int.from_bytes(r, 'little'), int.from_bytes(s, 'little'), get_poly_input(data)) % TAG_P).to_bytes(16, 'little')

def get_poly_input(cipher_text):
    data = cipher_text
    if len(cipher_text) & 0x0F:
        data += (b'\x00' * (16 - (len(cipher_text) & 0x0F)))
    data += (long_to_bytes(0, 8)[::-1])
    data += (long_to_bytes(len(cipher_text), 8)[::-1])
    return data

def generate_coeff(data):
    data_pad = data + pad16(data)
    coefficients = [int.from_bytes(data_pad[i:i+16] + b'\x01', 'little') for i in range(0, len(data_pad), 16)]
    return coefficients

def try_get_r(coefficients):
    F = GF(ACC_P)
    R = PolynomialRing(F, 'r') 
    r = R.gen()
    f = sum(coefficients[i] * r**(6 - i) for i in range(7))
    roots = f.roots(multiplicities=False)
    return roots

def recover_s(r, m_tag, m_cipher):
    m_nos_tag = int.from_bytes(generate_mac(r.to_bytes(16, 'little'), LITTLE_ZERO, m_cipher), 'little')
    s = (int.from_bytes(m_tag, 'little') - m_nos_tag) % TAG_P 
    return s

def xor_strings(xs, ys):
    return bytes(a ^ b for a, b in zip(xs, ys))

if ACC_M != ACC_P:
    raise Exception("ACC_M and ACC_P mismatch.") 

m1_cipher, m1_tag, m1_nonce = split_cipher_hex(M1_CIPHER_HEX)
m2_cipher, m2_tag, m2_nonce = split_cipher_hex(M2_CIPHER_HEX)
    
keystream = xor_strings(M1_PLAIN_HEX, m1_cipher)
forged_cipher = xor_strings(FT_PLAIN_HEX, keystream[:len(FT_PLAIN_HEX)])

if m1_nonce != m2_nonce:
    raise Exception("Nonce for input messages are different") 

m1_plain_tag = generate_mac(LITTLE_ONE, LITTLE_ZERO, m1_cipher)
m2_plain_tag = generate_mac(LITTLE_ONE, LITTLE_ZERO, m2_cipher)
    
m1_poly_input = get_poly_input(m1_cipher)
m2_poly_input = get_poly_input(m2_cipher)

m1_coefficients = generate_coeff(m1_poly_input)
m2_coefficients = generate_coeff(m2_poly_input)

coefficients_AB = [m1 - m2 for m1, m2 in zip(m1_coefficients, m2_coefficients)]
coefficients_BA = [m2 - m1 for m1, m2 in zip(m1_coefficients, m2_coefficients)]

m1_tag_int = int.from_bytes(m1_tag, 'little')
m2_tag_int = int.from_bytes(m2_tag, 'little')

recovered_r = None
recovered_s = None

for k in range(-4, 4):
    if recovered_r is not None and recovered_s is not None:
        break

    m1_k = -((m1_tag_int - m2_tag_int) + (TAG_P * k))
    test1_coefficients = coefficients_AB.copy()
    test1_coefficients.append(m1_k)

    test1_rcandidates = try_get_r(test1_coefficients)
    for rcandidate in test1_rcandidates:
        r_int = int(rcandidate.lift())
        if(r_int.bit_length() <= 128):
            test_s = recover_s(r_int, m1_tag, m1_cipher).to_bytes(16, 'little')
            test1_tag = generate_mac(r_int.to_bytes(16, 'little'), test_s, m1_cipher)
            test2_tag = generate_mac(r_int.to_bytes(16, 'little'), test_s, m2_cipher)
            if test1_tag == m1_tag and test2_tag == m2_tag:
                recovered_r = r_int.to_bytes(16,'little')
                recovered_s = test_s
                break
            
    m2_k = -((m2_tag_int - m1_tag_int) + (TAG_P * k))
    test2_coefficients = coefficients_AB.copy()
    test2_coefficients.append(m2_k)

    test2_rcandidates = try_get_r(test2_coefficients)
    for rcandidate in test2_rcandidates:
        r_int = int(rcandidate.lift())
        if(r_int.bit_length() <= 128):
            test_s = recover_s(r_int, m1_tag, m1_cipher).to_bytes(16, 'little')
            test1_tag = generate_mac(r_int.to_bytes(16, 'little'), test_s, m1_cipher)
            test2_tag = generate_mac(r_int.to_bytes(16, 'little'), test_s, m2_cipher)
            if test1_tag == m1_tag and test2_tag == m2_tag:
                recovered_r = r_int.to_bytes(16,'little')
                recovered_s = test_s
                break

if recovered_r is None or recovered_s is None:
    print("Could not recover inputs.")
    sys.exit(1)

print(f"Inputs recovered - r: {recovered_r.hex()}, s:{recovered_s.hex()}")

test1_tag = generate_mac(recovered_r, recovered_s, m1_cipher)
test2_tag = generate_mac(recovered_r, recovered_s, m2_cipher)
if test1_tag != m1_tag or test2_tag != m2_tag:
    print("Save error!")
    sys.exit(1)

forged_tag = generate_mac(recovered_r, recovered_s, forged_cipher)
forged_message = bytes.fromhex(forged_cipher.hex() + forged_tag.hex() + m1_nonce.hex())
print(forged_message.hex())
print("Success!")
