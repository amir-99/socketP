import socket
import sys
import threading
import time

szHeader = 12
initPort = 4580
myServer = "192.168.230.136"
myAddr = (myServer, initPort)
myFormat = "utf-8"
disMssg = "dis"

myClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myClient.setblocking(0)
myClient.settimeout(100)
myClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    myClient.connect(myAddr)
except socket.error:
    print(f"Unable to connect to server at {myServer}")
    sys.exit()
print("Connected")

def msgSend(msg):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    try:
        myClient.send(sendLength)
        myClient.send(msg)
    except socket.error:
        print("Unable to send data to server")
        sys.exit()

def clntSend():
    print ("type in your message.\ntype (dis) to disconnect\n")
    runningStatus = True
    while runningStatus:
        msg = input("your message:\n\t")
        if len(msg):
            msgSend(msg)
            if msg == disMssg:
                runningStatus = False
            time.sleep(0.01)


def clntRecv(conn, addr):
    rnClnt = True
    while rnClnt:
        try:
            msgLength = conn.recv(szHeader).decode(myFormat)
        except socket.error or socket.timeout:
            print(f"Unable to recive data from client at {addr}")
            rnClnt = False
            continue
        if msgLength:
            msgLength = int(msgLength)
            try:
                msg = conn.recv(msgLength).decode(myFormat)
            except socket.error or socket.timeout:
                print(f"Unable to recive data from server at {addr}")
                rnClnt = False
                continue
            print(f"Message from server at {addr} with size of {msgLength} :")
            print("\t" + msg)
            if msg == disMssg:
                rnClnt = False


rcvThread = threading.Thread(target=clntRecv, args=[myClient, myAddr])
rcvThread.daemon = True
rcvThread.start()
clntSend()