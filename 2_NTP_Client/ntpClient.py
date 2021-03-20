import socket
import ntplib
from time import ctime


def getTime():
    myNtpClnt = ntplib.NTPClient()
    response = myNtpClnt.request("pool.ntp.org")
    print(ctime(response.tx_time))


getTime()