import base64
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]
def gen(key):
    s = key.encode("utf-8")
    b64_token = base64.urlsafe_b64encode(s)
    print(b64_token.decode("utf-8"))

def bin2dec(string_num):
    return int(string_num, 2)

def dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])

import datetime
if __name__ == "__main__":
    a = None

    if a is not None:
        print("1111")
    else:
        print("22222")
