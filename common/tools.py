import uuid

def generateUUID():
    return uuid.uuid1()

def getTokenInfo(request,TOKENS_CACHE):
    token = request.headers.get("token")
    token_info = TOKENS_CACHE[token]

    return token_info

#检查对象是否为None，转换成”“
def NtoE(obj, replace_obj=""):
    if obj == None:
        return replace_obj

    return obj


#二进制转十进制
def bin2dec(string_num):
    return int(string_num, 2)

base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]

#十进制转二进制
def dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])

if __name__ == "__main__":
    a = "ddd"
    b = None
    print(NtoE(b))