from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


KEY = bytes([86, 66, 65, 49, 78, 85, 83, 54, 84, 56, 85, 73, 68, 50, 73, 54,
             79, 66, 70, 55, 49, 53, 56, 56, 57, 57, 67, 84, 52, 70, 51, 67])
IV = bytes([86, 66, 65, 49, 78, 85, 83, 54, 84, 56, 85, 73, 68, 50, 73, 54])


def encrypt_to_base64(s: str):
    s = '' if s is None else s
    aes = AES.new(KEY, AES.MODE_CBC, iv=IV)
    cipher_text = aes.encrypt(pad(s.encode(), aes.block_size))
    return b64encode(cipher_text).decode()


def decrypt_from_base64(s: str):
    aes = AES.new(KEY, AES.MODE_CBC, iv=IV)
    plain_text = unpad(aes.decrypt(b64decode(s)), aes.block_size)
    return plain_text.decode()
