import socket
import ntplib
from time import ctime


def getTime():
    myNtpClnt = ntplib.NTPClient()
    response = myNtpClnt.request("pool.ntp.org")
    print(response.to_data)
    print(ctime(response.tx_time))


getTime()