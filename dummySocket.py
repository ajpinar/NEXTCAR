import socket
import struct
import time


sock = socket.socket(socket.AF_INET,        # Internet
                     socket.SOCK_DGRAM)     # UDP

# Set the data, big endian format
dataFormat = '!Hdddiiddddddddddi'
##VEHICLE_ID = 12345
##SIMULATION_TIME_STEP = 0.1
##CURRENT_TIME = 234.567
##PREDICTION_HORIZON = 6
##PREDICTED_VEHICLE_VELOCITY = [34.5,35.1,36.2,38.5]
##PREDICTED_VEHICLE_X = [-1234.5432,-1234.5897,-1234.6666,-1234.7632]
##PREDICTED_VEHICLE_Y = [-1234.5432,-1234.5897,-1234.6666,-1234.7632]

##body = struct.pack(dataFormat,
##                      VEHICLE_ID,
##                      SIMULATION_TIME_STEP,
##                      CURRENT_TIME,
##                      PREDICTION_HORIZON,
##                      PREDICTED_VEHICLE_VELOCITY[0],
##                      PREDICTED_VEHICLE_VELOCITY[1],
##                      PREDICTED_VEHICLE_VELOCITY[2],
##                      PREDICTED_VEHICLE_VELOCITY[3],
##                      PREDICTED_VEHICLE_X[0],
##                      PREDICTED_VEHICLE_X[1],
##                      PREDICTED_VEHICLE_X[2],
##                      PREDICTED_VEHICLE_X[3],
##                      PREDICTED_VEHICLE_Y[0],
##                      PREDICTED_VEHICLE_Y[1],
##                      PREDICTED_VEHICLE_Y[2],
##                      PREDICTED_VEHICLE_Y[3])

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


remoteIP = '192.168.150.1'
computerIP = '192.168.150.10'
UDP_PORT = 5002

sock.bind((computerIP, UDP_PORT))

while(True):
    try:
        sock.sendto(body,  (remoteIP,  UDP_PORT) )
        print bytes(body)
        time.sleep(5)
    except KeyboardInterrupt:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()




