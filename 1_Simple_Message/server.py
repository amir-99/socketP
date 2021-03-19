import socket
import threading

szHeader = 12
initPort = 4580
myServer = socket.gethostbyname(socket.gethostname())
myAddr = (myServer, initPort)
myFormat = "utf-8"
disMssg = "dis"

bndServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bndServer.bind(myAddr)

connectins = list()
address = list()
runningThreads = list()

def clientResponse(conn, addr):
    print(f"{addr} Connected.")
    rnClnt = True
    while rnClnt:
        msgLength = conn.recv(szHeader).decode(myFormat)
        if msgLength:
            msgLength = int(msgLength)
            msg = conn.recv(msgLength).decode(myFormat)
            print(f"Message from {addr} with size of {msgLength} :")
            print("\t" + msg)
            if msg == disMssg:
                rnClnt = False
    conn.close()
    print(f"{addr} Disconnected.")
    address.remove(addr)
    connectins.remove(conn)
    print(f"Active Clients : {len(address)}")


def runServer():
    bndServer.listen(5)
    print(f"server is running on {myServer}:{initPort}")
    while True:
        tmpConn, tmpAddr = bndServer.accept()
        connectins.append(tmpConn)
        address.append(tmpAddr)
        clntThread = threading.Thread(target=clientResponse, args=(tmpConn, tmpAddr))
        clntThread.start()
        runningThreads.append(clntThread)
        print(f"Active Clients : {len(address)}")

runServer()