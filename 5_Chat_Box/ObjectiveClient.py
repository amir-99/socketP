import concurrent.futures
import sys
import pickle
import time
import socket
from queue import Queue
import select
from PIL import Image

C_FORMAT = "utf-8"
HEADER_LENGTH = 12

TXT_FLAG = "___TXT___"
PIC_FLAG = "___PIC___"
DIS_FLAG = "___DIS___"


class ObjectiveClient:

    running_stat = True

    def __init__(self, srvadd, port):
        self._SERVER_ADDR = srvadd
        self._PORT = port
        self._SERVER = (srvadd, port)
        self._SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set socket to non blocking
        self._SOCKET.setblocking(False)
        # set socket timeout to half an hour
        self._SOCKET.settimeout(1800)
        # enable reuse address
        self._SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # connect to socket
        try:
            self._conn = self._SOCKET.connect(self._SERVER)
        except socket.error:
            print(f"Can't connect to server at {self._SERVER_ADDR}:{self._PORT}")
            sys.exit()

        self.sendQueue = Queue()

    def rcv_msg(self, flag=TXT_FLAG):
        try:
            msg_length = self._conn.recv(HEADER_LENGTH)
            msg_length = msg_length.decode(C_FORMAT)
            msg_length = int(msg_length.strip())
        except socket.error:
            print("Unable to receive data!")
            self.running_stat = False
        else:
            if msg_length:
                if msg_length > 8192:
                    print("reciving large message")
                    milestone = 0
                    next_msg = b''
                    while True:
                        try:
                            tmp_msg = self._conn.recv(8192)
                            next_msg += tmp_msg
                            prog = int(len(next_msg)/msg_length)
                            if prog > milestone:
                                milestone = prog
                                print(f"{milestone*10}%...", end="", flush=True)
                            if len(next_msg) == msg_length:
                                break
                        except socket.error:
                            print("unable to receive message from server")
                            break
                else:
                    try:
                        msg = self._conn.recv(msg_length)
                    except socket.error:
                        print("unable to receive message from server")
                        self.running_stat = False
            if msg:
                if flag == PIC_FLAG:
                    next_msg = pickle.loads(msg)
                    next_msg.save(f"recivedimages/{time.time()}.png")
                else:
                    next_msg = msg.decode(C_FORMAT)
                    print(next_msg)
                return next_msg
            return 0

    def send_msg(self, msg, encoding=False):
        if encoding:
            msg = msg.encode(C_FORMAT)
        else:
            msg = pickle.dumps(msg)
        send_length = f'{len(msg):<{HEADER_LENGTH}}'.encode(C_FORMAT)
        try:
            self._conn.sendall(send_length)
            self._conn.sendall(msg)
        except socket.error:
            return 2
        else:
            return 0

    def get_input(self):
        while self.running_stat:
            msg = input("->")
            if msg:
                if msg == PIC_FLAG:
                    print("Enter the picture location (c to cancel) :")
                    while True:
                        loc = input(">>>")
                        if loc != "c":
                            try:
                                im = Image.open(loc)
                                self.sendQueue.put((PIC_FLAG, im))
                                break
                            except Exception:
                                print("wrong directory ! try again (c to cancel) ")
                        else:
                            break
                elif msg == "dis":
                    self.sendQueue.put((TXT_FLAG, DIS_FLAG))
                else:
                    self.sendQueue.put((TXT_FLAG, msg))

    def handle_client(self):
        inputs = [self._conn]
        outputs = [self._conn]
        prev_msg = ""
        msg = ""
        while self.running_stat:
            readable, _, _ = select.select(inputs, outputs, outputs)
            for soc in readable:
                if soc == self._conn:
                    if prev_msg == PIC_FLAG:
                        msg = self.rcv_msg(PIC_FLAG)
                    else:
                        msg = self.rcv_msg()
            
            try:
                flag, msg = self.sendQueue.get_nowait()
                if flag == PIC_FLAG:
                    self.send_msg(msg, encoding=False)
                else:
                    self.send_msg(msg)
            except Exception:
                pass

    def runclient(self):
        with concurrent.futures.ThreadPoolExecutor() as Executor:
            Executor.submit(self.get_input)
            Executor.submit(self.handle_client)
        while self.running_stat:
            pass


def main():
    addr = "192.168.1.10"
    port = 4580
    client = ObjectiveClient(addr, port)
    client.runclient()


if __name__ == "__main__":
    main()
