import socket
import threading
import concurrent.futures
import sys
from PIL import Image
import pickle

szHeader = 12   # Default Header Size
initPort = 4580     # Port number
myServer = socket.gethostbyname(socket.gethostname())       #get host ip
myAddr = (myServer, initPort)
myFormat = "utf-8"  #Coding format
disMssg = "dis"     #used to dsconnect Client
picMssg = "pic"     #used to notify picture transmission
maxTimeOut = 3600   #one hour


bndServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # disable set blockin
bndServer.setblocking(False)
    # set time out
bndServer.settimeout(maxTimeOut)
    # make socker reusable
bndServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    bndServer.bind(myAddr)
except socket.error:
    print(f"Couldn't Create the socket at {myAddr}")
    sys.exit()
except socket.timeout:
    print(f"Couldn't Create the socket at {myAddr}")
    sys.exit()

connectins = list()
address = list()
names = list()


def clientresponse(conn, addr):
    print(f"{addr} Connected.")
    msgsend('''successfully joind the chat
    type in your messages
    dis for disconnect
    --->
    ''', conn, addr)
    nameingStat = False
    msgsend("Enter Your Name : ", conn, addr)
    while not nameingStat:
        name, nameingStat = msgrcve(conn, addr)
        if name in names:
            msgsend("name taken, try again", conn, addr)
            nameingStat = False
        else:
            names.append(name)
    msgsend(f"joinde succesfully as {name}.", conn, addr)
    msgBroadCast(f"{name} joined chat", conn)
    rnClnt = True
    msgStat = True
    while rnClnt:
        msg, msgStat = msgrcve(conn, addr)
        if msgStat:
            if msg == disMssg:
                rnClnt == False
                break
            elif msg == picMssg:
                msgBroadCast(f"{name} is uploading a pic !", conn)
                picRcv(conn, addr, name)
            msg = f"{name} : " + msg
            msgBroadCast(msg, conn)

    msgBroadCast(f"{name} left chat", conn)
    conn.close()
    print(f"{addr} Disconnected.")
    address.remove(addr)
    connectins.remove(conn)
    names.remove(name)
    print(f"Active Clients : {len(address)}")


def msgrcve(conn, addr):
    opsanity = True
    try:
        msgLength = conn.recv(szHeader).decode(myFormat)
    except socket.error:
        print(f"Unable to recive data from client at {addr}")
        opsanity == False
        msg = ""
    except socket.timeout:
        print(f"Time out!")
        opsanity == False
        msg = ""
    finally:
        if msgLength:
                msgLength = int(msgLength)
                try:
                    msg = conn.recv(msgLength).decode(myFormat)
                except socket.error:
                    print(f"Unable to recive data from client at {addr}")
                    opsanity == False
                    msg == ""
                except socket.timeout:
                    print(f"Time Out!")
                    opsanity == False
                    msg = ""
    return (msg, opsanity)


def msgsend(msg, connClient, addrClient):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    try:
        connClient.send(sendLength)
        connClient.send(msg)
    except socket.error:
        print(f"Unable to send data to client at : {addrClient}")
        sys.exit()


def picRcv(conn, addr, name):
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
        print(f"reciving picture from {name}, size = {msgLength/(1024*1024)}MiB")
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
                    print("...100% | done !")
                    msgsend("pic uploaded to server! broadcast in progress !", conn, addr)
                
                    msgBroadCast(picMssg, conn)
                    picBroadCast(msg, conn)

                    




def msgBroadCast(msg, connClient):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    for index, conn in enumerate(connectins):
        if conn != connClient:
            try:
                conn.send(sendLength)
                conn.send(msg)
            except socket.error:
                print(f"Unable to send data to client at : {address[index]}")
                sys.exit()


def picBroadCast(img, connClient):
    sendLength = f'{len(img):<{szHeader}}'.encode(myFormat)
    for index, conn in enumerate(connectins):
        if conn != connClient:
            try:
                conn.send(sendLength)
                conn.send(img)
            except socket.error:
                print(f"Unable to send pic to client at : {address[index]}")
                sys.exit()


def serverhandle(executor):
    handle = input()
    if handle == 'ls':
        listconnections()
    else:
        pass

def listconnections():
    print(f"currently {len(address)} active connections.")
    for name, add in zip(names, address):
        print(f"{name} on {add}")


def runserver():
    bndServer.listen(5)
    print(f"server is running on {myServer}:{initPort}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=250) as executor:
        executor.submit(serverhandle, executor)
        while True:
            if len(address)<250:
                try:
                    tmpConn, tmpAddr = bndServer.accept()
                except socket.error:
                    print("Couldn't accept connection!")
                    sys.exit()
                connectins.append(tmpConn)
                address.append(tmpAddr)
                executor.submit(clientresponse, tmpConn, tmpAddr)
                print(f"Active Clients : {len(address)}")


runserver()
