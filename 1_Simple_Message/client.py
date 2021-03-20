import socket
import sys

szHeader = 12
initPort = 4580
myServer = "192.168.230.136"
myAddr = (myServer, initPort)
myFormat = "utf-8"
disMssg = "dis"

myClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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


print ("type in your message.\ntypr (dis) to disconnect\n")
runningStatus = True
while runningStatus:
    msg = input("your message:\n\t")
    if len(msg):
        msgSend(msg)
        if msg == disMssg:
            runningStatus = False