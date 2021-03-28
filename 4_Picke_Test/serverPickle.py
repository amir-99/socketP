import socket
import pickle
import concurrent.futures
import sys
from PIL import Image

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
except socket.error:
    print(f"Couldn't Create the socket at {myAddr}")
    sys.exit()
except socket.timeout:
    print("timeout !")
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
    msgsend("successfully connected to server", conn, addr)
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
        if msgLength:
            msgLength = int(msgLength)
            if msgLength>4096:
                msg = b''
                mileStone = 0
                print("reciving image:\n progress: ",end=" ")
                while True:
                    try:
                        msgSeg = conn.recv(2048)
                    except socket.error:
                        print(f"Unable to recive data from client at {addr}")
                        rnClnt = False
                        continue
                    msg += msgSeg
                    progress = int((len(msg)/msgLength)*10)
                    if progress> mileStone:
                        mileStone = progress
                        print(f"...{mileStone*10}%", end="", flush=True)
                    if len(msg) == msgLength:
                        print("...100% | done !")
                        break


                print(f"Message from {addr} with size of {msgLength} :")
            im = pickle.loads(msg)
            im.show()
            msgsend("dis", conn, addr)

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
    bndServer.listen()
    print(f"server is running on {myServer}:{initPort}")
    try:
        tmpConn, tmpAddr = bndServer.accept()
    except socket.error:
        print("Couldn't accept connection !")
        sys.exit()
    clientresponse(tmpConn, tmpAddr)
    print(f"Client conected !")


if __name__ == "__main__":
    runserver()
