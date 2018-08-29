"""

Author: Sam Celani

File:   dummySocket.py

Description:

    This file simulates having received data,
    and sends it over a socket to the MABX.
    
    It is part of the ARPA-E Project: NEXTCAR.
    
"""

###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:
    
    import socket       ##  Used to send data over a socket connection
    import struct       ##  Used to pack data before sending
    import time         ##  Used to sleep between sending messages
    
except Exception as ex:
    print ex
    exit()

###########################################################

#
#   SOCKET AND DATA
#

##  Define a socket
sock = socket.socket(socket.AF_INET,        # Internet
                     socket.SOCK_DGRAM)     # UDP

##  Determine the format of the data
dataFormat = '!Hdddiiddddddddddi'

##  Pack the data into bytes
body = struct.pack(dataFormat,
                   123,
                   0.1,
                   1.6,
                   5,
                   16,
                   5,
                   35,
                   35,
                   35,
                   35,
                   35,
                   25,
                   25,
                   25,
                   25,
                   25,
                   1)

##  IP of MABX
remoteIP = '192.168.150.1'

##  IP of computer
computerIP = '192.168.150.10'

##  Port
UDP_PORT = 5002

##  Bind port to IP of computer
sock.bind((computerIP, UDP_PORT))

while True:
    try:
        ##  Send data over socket to UDP_PORT of MABX IP
        sock.sendto(body,  (remoteIP,  UDP_PORT) )
        ##  Print data
        print bytes(body)
        ##  Sleep for five seconds to avoid sending constant messages
        time.sleep(5)
    except KeyboardInterrupt:

        ##  This code block came from Pilot
        ##  Shuts down the socket
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

