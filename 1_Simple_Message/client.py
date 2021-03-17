import socket

szHeader = 12
initPort = 4580
myServer = "192.168.230.136"
myAddr = (myServer, initPort)
myFormat = "utf-8"
disMssg = "dis"

myClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myClient.connect(myAddr)
print("Connected")

def msgSend(msg):
    msg = msg.encode(myFormat)
    sendLength = f'{len(msg):<{szHeader}}'.encode(myFormat)
    print(sendLength)
    print(len(sendLength))
    myClient.send(sendLength)
    myClient.send(msg)
    

msgSend("HI")
print("Hi")
input()
print("aaaa")
msgSend("asd spksdc fpj psdjc uheadopcj me")
input()
print("dis")
msgSend("dis")