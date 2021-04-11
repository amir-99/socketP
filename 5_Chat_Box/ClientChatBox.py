import concurrent.futures
import sys
import pickle
import time
import socket
from queue import Queue
import select
from PIL import Image
import time
import os

C_FORMAT = "utf-8"
HEADER_LENGTH = 12

TXT_FLAG = "___TXT___"
PIC_FLAG = "___PIC___"
DIS_FLAG = "___DIS___"

running_stat = True


def send_msg(conn, msg, encoding=True):
    if encoding:
        msg = msg.encode(C_FORMAT)
    send_length = f'{len(msg):<{HEADER_LENGTH}}'.encode(C_FORMAT)
    try:
        conn.sendall(send_length)
        conn.sendall(msg)
    except socket.error:
        return 2
    else:
        return 0


def recv_msg(conn):
    global running_stat
    next_msg = ""
    previous_msg = ""
    while running_stat:
        try:
            msg_length = conn.recv(HEADER_LENGTH)
            msg_length = msg_length.decode(C_FORMAT)
        except socket.error:
            print("Unable to receive data!")
            sys.exit()
        else:
            msg_length = int(msg_length.strip())
            if msg_length:
                previous_msg = next_msg
                if msg_length > 8192:
                    print("reciving large message")
                    milestone = 0
                    next_msg = b''
                    while True:
                        try:
                            tmp_msg = conn.recv(8192)
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
                    previous_msg = next_msg
                    try:
                        msg = conn.recv(msg_length)
                    except socket.error:
                        print("unable to receive message from server")
                        running_stat = False
            if msg:
                if previous_msg == PIC_FLAG:
                    next_msg = pickle.loads(msg)
                    next_msg.save(os.path.join(os.getcwd(), "recivedimages", f"pic_{time.time()}.jpg"))
                else:
                    next_msg = msg.decode(C_FORMAT)
                    print(next_msg)


def sen_handler(conn):
    global running_stat
    while running_stat:
        msg = input("->")
        if msg:
            if msg == PIC_FLAG:
                print("Enter the picture location (c to cancel) :")
                while True:
                    loc = input(">>>")
                    if loc != "c":
                        try:
                            im = Image.open(loc)
                            im = pickle.dumps(im)
                            send_msg(conn, PIC_FLAG)
                            send_msg(conn, im, encoding=False)
                            print("Sent the specifaied image to server")
                            break
                        except Exception:
                            print("wrong directory ! try again (c to cancel) ")
                    else:
                        break
            elif msg == "dis":
                send_msg(conn, DIS_FLAG)
                running_stat = False
            else:
                send_msg(conn, msg)


def run_client():
    SERVER_ADDR = "192.168.1.10"
    SERVER_PORT = 4580
    SERVER = (SERVER_ADDR, SERVER_PORT)
    chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set to non blocking
    chat_client.setblocking(False)
    # set socket to reusable
    chat_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # set time out to half an hour
    chat_client.settimeout(1800)

    try:
        chat_client.connect(SERVER)
        print("Waiting for server reply !")
    except socket.error:
        print(f"Unable to connect to server at {SERVER}")
        sys.exit()

    with concurrent.futures.ThreadPoolExecutor() as Executor:
        Executor.submit(recv_msg, chat_client)
        Executor.submit(sen_handler, chat_client)
    while running_stat:
        pass


if __name__ == "__main__":
    run_client()
