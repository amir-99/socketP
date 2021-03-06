import concurrent.futures
import pickle
import time
import socket
from queue import Queue
import select
from PIL import Image
import os

C_FORMAT = "utf-8"
HEADER_LENGTH = 12

TXT_FLAG = "___TXT___"
PIC_FLAG = "___PIC___"
DIS_FLAG = "___DIS___"


class Client:

    running_stat = True

    def __init__(self, addr, conn, name="Name not set"):
        self._addr = addr
        self._conn = conn
        self.name = name
        self.msgQueue = Queue()
        self.picQueue = Queue()
        self.client_running_stat = True
        self.linked_server = None

    def send_msg(self, msg, encoding=True):
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

    def get_address(self):
        return self._addr

    def run_client(self, linked_server):
        self.linked_server = linked_server
        self.send_msg("Successfully Joined The Chat!")

        inputs = [self._conn]
        outputs = [self._conn]

        while self.name == "Name not set":
            self.send_msg("Enter a unique name:")
            tmp_name = self.rcv_msg()
            stat = True
            for client_inst in self.linked_server.Clients:
                if tmp_name == client_inst.name:
                    stat = False
                    self.send_msg("Name taken !")
                    break
            if stat:
                self.name = tmp_name
        self.send_msg(f"joined as {self.name}")
        self.broadcast_msg(f"{self.name} has joined the chat!")
        new_msg = None
        while self.running_stat & self.client_running_stat:
            readable, _, _ = select.select(inputs, outputs, outputs)
            for con in readable:
                if con == self._conn:
                    previous_msg = new_msg
                    if previous_msg == PIC_FLAG:
                        self.broadcast_msg(f"{self.name} is sending a picture !")
                        new_msg = self.rcv_msg(flag=PIC_FLAG)
                        self.broadcast_msg(new_msg, PIC_FLAG)
                    else:
                        new_msg = self.rcv_msg()
                        if new_msg == DIS_FLAG:
                            self.client_running_stat = False
                            print(f"{self.name} left !")
                            self.broadcast_msg(f"{self.name} lef the chat !")
                            print(f"Active clients : {len(self.linked_server.Clients)-1}")
                            self.linked_server.Clients.remove(self)
                        else:
                            new_msg = f"{self.name} : " + new_msg
                            self.broadcast_msg(new_msg)
            try:
                flag, msg = self.msgQueue.get_nowait()
                if flag == TXT_FLAG:
                    self.send_msg(msg)
                elif flag == PIC_FLAG:
                    self.send_msg(msg, encoding=False)
            except Exception:
                pass

    def rcv_msg(self, flag=TXT_FLAG):
        msg_length = self._conn.recv(HEADER_LENGTH)
        msg_length = msg_length.decode(C_FORMAT)
        msg_length = int(msg_length.strip())
        if msg_length:
            if msg_length > 8192:
                print(f"reciving large message from {self.name}")
                milestone = 0
                msg = b''
                while True:
                    try:
                        tmp_msg = self._conn.recv(8192)
                        msg += tmp_msg
                        prog = int(len(msg)/msg_length)
                        if prog > milestone:
                            milestone = prog
                            print(f"{milestone*10}%...", end="", flush=True)
                        if len(msg) == msg_length:
                            break
                    except socket.error:
                        print(f"unable to receive message from client {self._addr}. Closing Connection")
                        self.client_running_stat = False
                        return None
            else:
                try:
                    msg = self._conn.recv(msg_length)
                except socket.error:
                    print(f"unable to receive message from client {self._addr}. Closing Connection")
                    self.client_running_stat = False
                    return None
            if flag == PIC_FLAG:
                msg = pickle.loads(msg)
                msg.save(os.path.join(os.getcwd(), "recivedimages", f"{self.name}_{time.time()}.jpg"))
            elif flag == TXT_FLAG:
                msg = msg.decode(C_FORMAT)
        return msg

    def broadcast_msg(self, msg, flag=TXT_FLAG):
        for client_inst in self.linked_server.Clients:
            if client_inst != self:
                client_inst.msgQueue.put((flag, msg))

    def __str__(self):
        return f"Client {self.name} at address {self._addr}"


class Server:
    def __init__(self, **kwargs):
        self._Port = kwargs['port']
        self._SetBlocking = kwargs['s_b']
        self._HOSTNAME = kwargs['hostname']
        self._ReUse = kwargs['r_u']
        self._Addr = (self._HOSTNAME, self._Port)
        # Create socket
        self._Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set blocking status
        self._Socket.setblocking(self._SetBlocking)
        # Reuse address status
        self._Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self._ReUse)
        # set timeout equal to half an hour
        self._Socket.settimeout(1800)

        self.Clients = list()
        self.running_status = True

    def bind(self):
        try:
            self._Socket.bind(self._Addr)
            print(f"Server running at {self._HOSTNAME}:{self._Port}")
        except socket.timeout:
            return 1
        else:
            return 0

    def list_connections(self):
        for count, cln in enumerate(self.Clients, start=1):
            print(f"{count}_ {cln.name} at {cln.get_address()}", flush=True)

    def run_server(self, worker_thread=250, listen_queue_length=5):
        self._Socket.listen()

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_thread) as Exec:

            while self.running_status:
                if len(self.Clients) < 250:
                    try:
                        tmp_conn, tmp_addr = self._Socket.accept()
                        tmp_client = Client(tmp_addr, tmp_conn)
                        try:
                            Exec.submit(tmp_client.run_client, self)
                            self.Clients.append(tmp_client)
                        except Exception as e:
                            print(f"Can not create new client. Error : {e}")
                    except socket.error:
                        print("Can't accept new connections !")
                    else:
                        print(f"New client at {tmp_addr} | Active clients = {len(self.Clients)}")
                else:
                    pass


if __name__ == "__main__":
    host_addr = "192.168.1.10"
    host_port = 4580
    set_blocking = False
    reuse_stat = True

    server_inst = Server(hostname=host_addr, port=host_port, s_b=set_blocking, r_u=reuse_stat)
    server_inst.bind()
    server_inst.run_server()
