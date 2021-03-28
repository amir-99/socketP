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
picMssg = "pic"     #used to notify picture transmission
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
        myClient.sendall(sendLength)
        myClient.sendall(msg)
    except socket.error:
        print("Unable to send data to server")
        sys.exit()


def sendpic():
    flag = True
    while flag:
        loc = input("Enter the picture location :")
        flag = False
        try:
            im = Image.open(loc)
        except Exception :
            print("Unable to read from the specified directory try again !")
            flag = True
    msg = pickle.dumps(im)
    if len(msg):
        sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
        try:
            myClient.sendall(sendLength)
            myClient.sendall(msg)
        except socket.error:
            print("Unable to send picture to server")
            sys.exit()
        finally:
            print("sent image")    

#run client
def clntSend():
    runningStatus = True
    while runningStatus:
        msg = input()
        if len(msg):
            msgSend(msg)
            if msg == picMssg:
                sendpic()
            elif msg == disMssg:
                msgSend(msg)
                runningStatus = False
            time.sleep(0.01)    # use delay to make sure the response arrives first


#Recive Picture From Server !
def picRcv(conn, addr):
    try:
        msgLength = conn.recv(szHeader).decode(myFormat)
    except socket.error:
        print(f"Unable to recive data from client at {addr}")
        sys.exit()
    except socket.timeout:
        print("Time Out!")
        sys.exit()
    if msgLength:
        msgLength = int(msgLength)
        print(f"reciving picture with size of = {round(msgLength/(1024*1024), 2)}MiB")
        if msgLength>8192:
            msg = b''
            mileStone = 0
            print("reciving image:\n progress: ",end=" ")
            while True:
                try:
                    msgSeg = conn.recv(80192)
                except socket.error:
                    print(f"Unable to recive picture from client at {addr}")
                    continue
                msg += msgSeg
                progress = int((len(msg)/msgLength)*10)
                if progress> mileStone:
                    mileStone = progress
                    print(f"...{mileStone*10}%", end="", flush=True)
                if len(msg) == msgLength:
                    print("...100% | done !", flush=True)
                    break
            img = pickle.loads(msg)
            return img
                

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
        except socket.timeout:
            print("Time Out!")
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
            except socket.timeout:
                print("Time Out!")
                rnClnt = False
                continue
            print(msg)
            if msg == picMssg:
                im = picRcv(conn, addr)
                inA = input ("do you want to see the image(y/n) :")
                if inA == "y":
                    im.show()
            elif msg == disMssg:
                rnClnt = False

# make a thread for receving data from server
# so that the input is not interupted
rcvThread = threading.Thread(target=clntRecv, args=[myClient, myAddr])
rcvThread.daemon = True
rcvThread.start()
clntSend()
