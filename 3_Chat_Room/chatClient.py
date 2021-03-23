import socket
import sys
import threading
import time

szHeader = 12   # Default Header Size
initPort = 4580     # Port number
myServer = "127.0.0.1"
myAddr = (myServer, initPort)
myFormat = "utf-8"  #Coding format
disMssg = "dis"     #used to dsconnect Client
maxTimeOut = 3600   #one hour


myClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # disable set blockin
myClient.setblocking(False)
    # set time out
myClient.settimeout(maxTimeOut)
    # make socker reusable
myClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    myClient.connect(myAddr)
except socket.error:
    print(f"Unable to connect to server at {myServer}")
    sys.exit()
print("Waiting for server reply!")

#Send Messages to the server!
#send the headar then the message!
def msgSend(msg):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    try:
        myClient.send(sendLength)
        myClient.send(msg)
    except socket.error:
        print("Unable to send data to server")
        sys.exit()


#run client
def clntSend():
    runningStatus = True
    while runningStatus:
        msg = input()
        if len(msg):
            msgSend(msg)
            if msg == disMssg:
                runningStatus = False
            time.sleep(0.01)    # use delay to make sure the response arrives first


#recive data from server
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
            print(msg)
            if msg == disMssg:
                rnClnt = False

# make a thread for receving data from server
# so that the input is not interupted
rcvThread = threading.Thread(target=clntRecv, args=[myClient, myAddr])
rcvThread.daemon = True
rcvThread.start()
clntSend()
