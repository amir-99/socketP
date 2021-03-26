import socket
import sys
import threading
import time
from PIL import Image
import pickle

szHeader = 12   # Default Header Size
initPort = 4580     # Port number
myServer = "127.0.0.1"
myAddr = (myServer, initPort)
myFormat = "utf-8"  #Coding format
disMssg = "dis"     #used to dsconnect Client

myClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # disable set blockin
myClient.setblocking(False)
    # set time out of 2 min
myClient.settimeout(120)
    # make socker reusable
myClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    myClient.connect(myAddr)
except socket.error:
    print(f"Unable to connect to server at {myServer}")
    sys.exit()
except socket.timeout():
    print("Time out!")
    sys.exit()

#Send Messages to the server!
#send the headar then the message!
def msgSend(msg):
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    try:
        myClient.send(sendLength)
        myClient.sendall(msg)
    except socket.error:
        print("Unable to send data to server")
        sys.exit()


#run client
def clntSend():
    im = Image.open("/home/amir/WallPapers/tstpic.png")
    msg = pickle.dumps(im)
    if len(msg):
        msgSend(msg)
        print("sent image")

#recive data from server
def clntRecv(conn, addr):
    rnClnt = True
    while rnClnt:
        try:
            msgLength = conn.recv(szHeader).decode(myFormat)
        except socket.error:
            print(f"Unable to recive data from client at {addr}")
            rnClnt = False
            continue
        if msgLength:
            msgLength = int(msgLength)
            try:
                msg = conn.recv(msgLength).decode(myFormat)
            except socket.error:
                print(f"Unable to recive data from server at {addr}")
                rnClnt = False
                continue
            print(f"Message from server at {addr} with size of {msgLength} :")
            print("\t" + msg)
            if msg == disMssg:
                rnClnt = False

# make a thread for receving data from server
# so that the input is not interupted
rcvThread = threading.Thread(target=clntRecv, args=[myClient, myAddr])
rcvThread.daemon = False
rcvThread.start()
clntSend()