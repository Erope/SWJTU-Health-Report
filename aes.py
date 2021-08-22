import random, base64, string
from Crypto.Cipher  import AES

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

head = ''.join(random.sample(string.ascii_letters + string.digits, 32))
head += ''.join(random.sample(string.ascii_letters + string.digits, 32))
iv = ''.join(random.sample(string.ascii_letters + string.digits, 16))

def encryptAES(pwd, salt):
    data = pad(head+pwd)
    # 字符串补位
    cipher = AES.new(salt.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
    encryptedbytes = cipher.encrypt(data.encode('utf8'))
    # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
    encodestrs = base64.b64encode(encryptedbytes)
    # 对byte字符串按utf-8进行解码
    enctext = encodestrs.decode('utf8')
    return enctext
