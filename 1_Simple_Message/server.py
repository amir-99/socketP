import socket
import threading
import concurrent.futures
import sys

szHeader = 12   # Default Header Size
initPort = 4580     # Port number
myServer = socket.gethostbyname(socket.gethostname())       #get host ip
myAddr = (myServer, initPort)
myFormat = "utf-8"  #Coding format
disMssg = "dis"     #used to dsconnect Client
maxConnections = 250

bndServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # disable set blockin
bndServer.setblocking(False)
    # set time out of 2 min
bndServer.settimeout(120)
    # make socker reusable
bndServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    bndServer.bind(myAddr)
except socket.error or socket.timeout:
    print(f"Couldn't Create the socket at {myAddr}")
    sys.exit()

connectins = list()
address = list()
runningThreads = list()

# this func handles clients
# 1s receives headers
#then receives the message
#and finally send back a confirmation
def clientresponse(conn, addr):
    print(f"{addr} Connected.")
    msgsend("successfully connected to server\nType in your messages (dis for disconnect)", conn, addr)
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
            #create and send bback the response
            respMsg = f"recived following message : ({msg})"
            msgsend(respMsg, conn, addr)
    conn.close()
    print(f"{addr} Disconnected.")
    address.remove(addr)
    connectins.remove(conn)
    print(f"Active Clients : {len(address)}")


def msgsend(msg, connClient, addrClient):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    try:
        connClient.send(sendLength)
        connClient.send(msg)
    except socket.error:
        print(f"Unable to send data to client at : {addrClient}")


def runserver():
    bndServer.listen(5)
    print(f"server is running on {myServer}:{initPort}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=maxConnections) as executor:
        while True:
            if len(address)<maxConnections:
                try:
                    tmpConn, tmpAddr = bndServer.accept()
                except socket.error:
                    print("Couldn't accept connection !")
                    sys.exit()
                connectins.append(tmpConn)
                address.append(tmpAddr)
                thrd = executor.submit(clientresponse, tmpConn, tmpAddr)
                runningThreads.append(thrd)
                print(f"Active Clients : {len(address)}")
runserver()
