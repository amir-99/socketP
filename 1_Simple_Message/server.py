import socket
import threading
import sys

szHeader = 12
initPort = 4580
myServer = socket.gethostbyname(socket.gethostname())
myAddr = (myServer, initPort)
myFormat = "utf-8"
disMssg = "dis"

bndServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bndServer.setblocking(0)
bndServer.settimeout(100)
bndServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    bndServer.bind(myAddr)
except socket.error:
    print(f"Couldn't Create the socket at {myAddr}")
    sys.exit()

connectins = list()
address = list()
runningThreads = list()

def clientResponse(conn, addr):
    print(f"{addr} Connected.")
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
                print(f"Unable to recive data from client at {addr}")
                rnClnt = False
                continue
            print(f"Message from {addr} with size of {msgLength} :")
            print("\t" + msg)
            if msg == disMssg:
                rnClnt = False
            respMsg = f"recived following message : ({msg})"
            msgSend(respMsg, conn, addr)
    conn.close()
    print(f"{addr} Disconnected.")
    address.remove(addr)
    connectins.remove(conn)
    print(f"Active Clients : {len(address)}")


def msgSend(msg, connClient, addrClient):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    try:
        connClient.send(sendLength)
        connClient.send(msg)
    except socket.error:
        print(f"Unable to send data to client at : {addrClient}")
        sys.exit()


def runServer():
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
        clntThread = threading.Thread(target=clientResponse, args=(tmpConn, tmpAddr))
        clntThread.daemon = True
        clntThread.start()
        runningThreads.append(clntThread)
        print(f"Active Clients : {len(address)}")

runServer()