import socket
import threading
import sys

szHeader = 12   # Default Header Size
initPort = 4580     # Port number
myServer = socket.gethostbyname(socket.gethostname())       #get host ip
myAddr = (myServer, initPort)
myFormat = "utf-8"  #Coding format
disMssg = "dis"     #used to dsconnect Client
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
except socket.error or socket.timeout:
    print(f"Couldn't Create the socket at {myAddr}")
    sys.exit()

connectins = list()
address = list()
names = list()
runningThreads = list()


def clientresponse(conn, addr):
    print(f"{addr} Connected.")

    nameingStat = False
    while not nameingStat:
        name, nameingStat = msgrcve(conn, addr)
        names.append(name)
    msgBroadCast(f"{name} joined chat", conn)
    rnClnt = True
    msgStat = True
    while rnClnt:
        msg, msgStat = msgrcve(conn, addr)
        if msgStat:
            if msg == disMssg:
                rnClnt == False
                break
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
    except socket.error or socket.timeout:
        print(f"Unable to recive data from client at {addr}")
        opsanity == False
        msg = ""
    finally:
        if msgLength:
                msgLength = int(msgLength)
                try:
                    msg = conn.recv(msgLength).decode(myFormat)
                except socket.error or socket.timeout:
                    print(f"Unable to recive data from client at {addr}")
                    opsanity == False
                    msg == ""
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



def runserver():
    bndServer.listen(5)
    print(f"server is running on {myServer}:{initPort}")
    while True:
        try:
            tmpConn, tmpAddr = bndServer.accept()
        except socket.error:
            print("Couldn't accept connection !")
            sys.exit()
        connectins.append(tmpConn)
        address.append(tmpAddr)
        #create a thread for each client in order to run the module cocurently
        clntThread = threading.Thread(target=clientresponse, args=(tmpConn, tmpAddr))
        # enable daemon feature to terminate the thread with termination of main thread
        clntThread.daemon = True
        clntThread.start()
        runningThreads.append(clntThread)
        print(f"Active Clients : {len(address)}")


runserver()
