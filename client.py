from socket import *
import threading
import time
import sys
import alice, bob
# from simplecrypt import encrypt, decrypt, DecryptionException

key = "lemon-tea"
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher():

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self._pad(AESCipher.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')



def send(sock):
    while True:
        try:
            aes = AESCipher(key)
            sendData = aes.encrypt(input()).encode('utf-8')
            # sendData = encrypt(key, input())
            sock.send(sendData)
        except:
            continue


def receive(sock):
    while True:
        recvData = sock.recv(1024)
        try:
            aes = AESCipher(key)
            print('%s :'%opp_id, aes.decrypt(recvData))
            # print('%s :'%opp_id, decrypt(key, recvData).decode('utf-8'))
        except DecryptionException as e:
            print(e)


port = int(sys.argv[1])

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect(('45.76.54.218', port))

user_id = str(input("ID: "))
clientSock.send(user_id.encode('utf-8'))

# user_list = clientSock.recv(1024).decode('utf-8')
# print("USER LIST: {}".format(user_list))

opp_id = str(input("연결 대상자의 ID를 입력하십시오(교신을 대기하려면 공백 그대로 입력): "))

if opp_id:
    print(key)
    clientSock.send(opp_id.encode('utf-8'))

    print("교신 대상과 COMM 터널 수립 완료. QKD 양자 키 분배를 시작합니다.")
    key = str(alice.key())
    time.sleep(1)
    print("편광 필터 배열, A.L.I.C.E KEY 생성을 완료했습니다. 큐비트 전송 시퀀스에 돌입합니다.")
    time.sleep(1)
    print("Tokyo 메인 서버에 피클링된 큐비트와 회로를 전송 중입니다. 기다려 주십시오...")
    time.sleep(1)
    with open('alice.laser', 'rb') as file:
        clientSock.send(file.read())
else:
    clientSock.send("~".encode('utf-8'))
    print("교신 대상 ID 공백. 교신 대기.")
    opp_id = clientSock.recv(1024).decode('utf-8')
    print("%s로부터의 교신 요청입니다. 수락합니다."%opp_id)
    time.sleep(1)
    print("%s로부터 B.O.B KEY, 큐비트, 편광 필터와 회로를 수신합니다..."%opp_id)
    time.sleep(1)
    laser = clientSock.recv(2048)
    with open('bob.laser', 'wb') as file:
        file.write(laser)
    key = str(bob.key())


print("QKD 완료. 양자 채널이 구성되었습니다. LINK START!")
print("Final AES Encryption Key: ", key)


sender = threading.Thread(target=send, args=(clientSock,))
receiver = threading.Thread(target=receive, args=(clientSock,))

sender.start()
receiver.start()

while True:
    time.sleep(1)
    pass