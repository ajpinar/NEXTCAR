import threading
import pika
import os
import struct
import socket

# set to True to use Tony's CloudAMQP service
useCloudAMQP = True

# URL for Tony's AMQP Server
urlT = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'

# URL for Sam's AMQP Server
urlS = None

# Sam's scripts server ip
c2vProd = '141.219.205.25'

# Kuilin's server ip
kuilin = '141.219.181.216'

adT = True
adF = False

class Publisher:

    def __init__(self, SERVERIP, CREDENTIALS, IP, PORT, LOGNAME, ROUTING_KEY):

        """
        Parmeters:

        SERVERIP=   (string)    The IP address of the server
        CREDENTIALS= (pika.plaincredentials) credentials to log into cloud server
        IP      =   (string)    The IP address for the UDP connection to the MABX (i.e. "127.0.0.1").
        PORT    =   (int)       The port for the UDP socket.
        LOGNAME =   (string)    The name of the Rabbit MQ logger exchange.
        """

        # Set the Rabbit MQ parameters
        self.serverip = SERVERIP
        self.credentials = CREDENTIALS
        if useCloudAMQP:
            print "Using CloudAMQP"
            self.params = pika.URLParameters(urlT)
        else:
            print "Using local server"
            self.params = pika.ConnectionParameters(self.serverip,
                                    5672,
                                    '/',
                                    self.credentials)                # Set Pika parameters
        self.connection = None                                      # Declare Connection field
        self.channel = None                                         # Declare Channel object
        self.logName = LOGNAME                                      # Log name should match the Publisher's name
        self.RoutingKey = ROUTING_KEY;

        # Set the UDP parametes
        self.keep_running = False                                   # Flag for the UDP Listening loop
        self.UDP_IP = IP
        self.UDP_PORT = PORT
        self.sock = socket.socket(socket.AF_INET,                   # Internet
                     socket.SOCK_DGRAM)                             # UDP

    def start(self):
        """
        Start the UDP listener in a separate thread.
        """

        self.keep_running = True                                    # Set running flag to true
        self.th = threading.Thread(target=self.listenSocket)
        self.th.daemon = True                                       # Thread will terminate with the main
        self.th.start()
        self.th.join(0)
        
    def listenSocket(self):
        """
        Start the UDP Socket
        """

        # Bind to the listening socket.AF_INET
        # It may be good to add a timeout routine later
        try:
            self.sock.settimeout(10.0)
            self.sock.bind((self.UDP_IP, self.UDP_PORT))
            print("  UDP %s::%i Socket Bound" % (self.UDP_IP, self.UDP_PORT))
        
            while self.keep_running:
                try:
                    pass
                    data, addr = self.sock.recvfrom(1024)           # buffer size is 1024 bytes
                except socket.timeout as e:
                    if self.keep_running:
                        print("  UDP %s::%i Timeout Occurred" % (self.UDP_IP, self.UDP_PORT))
                    else:
                        pass
                else:
                    self.callback(data)

        finally:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print("  UDP %s::%i Shutdown" % (self.UDP_IP, self.UDP_PORT))
            #print("  UDP %s::%i Shutdown" % (101, 202)) #TONY WAS HERE

    def callback(self, data):
        """
        Send the data over the Rabbit MQ Connection
        """

        #print len(data)

        # establish the RabbitMQ connection with input parameters
        self.connection = pika.BlockingConnection(self.params)

        self.channel = self.connection.channel()

        # The fanout exchange broadcasts all the messages it receives to all the queues it knows.
        # That is what we need for our logger.
        # Tony changed to 'topic' to work with Kuilin's group
        self.channel.exchange_declare(exchange=self.logName,
                                      exchange_type='topic',
                                      auto_delete=True)

        #TONY WAS HERE
        #CONVERT THE DATA BEFORE SENDING
        
        #data_tuple = struct.unpack("<hddhdddddddddddd", data)

        ip = '141.219.212.72'       # I don't know how to make strings in Simulink, so the IP is added here

        # staticData = '001,141.219.212.72,2,1,1,FFFFFF,@,'  ## Data packet in Simulink was updated to include the static data

        #fmt = "<hddhdddddddddddd"                 # From Tony, IO_Wrapper -> MABX_PLATFORM -> UDP -> RabbitMQ_Packing
        fmt = "<HddHHdiddddd?ddddd?dddddddddi"     # From Data_Interface_for_Communications_06/27/2018.xlsx
        fmt2 = "<HsddHHcdiddddd?ddddd?dddddddddi"     # From Data_Interface_for_Communications_06/27/2018.xlsx
        print fmt.count('?') + 2 * fmt.count('H') + 8 * fmt.count('d') + 4 * fmt.count('i')

##        try:
##            dynamicData = struct.unpack(fmt,data)
##            dynamicData = dynamicData[:-2]
##        except e:
##            print('Format of bytestream didn''t match',fmt)
##            dynamicData = str(data)         # the problem here is that I don't know what this data looks like
##                                            # or what it is at all
##            print e
##        else:
##            dynamicData = str(dynamicData.insert(1,ip)).replace(' ','').replace("'","")[1:-1]
        raw_data = list(struct.unpack(fmt,data))
        raw_data.insert(1,ip)
        raw_data.insert(6,'@')
        #dynamicData = str(raw_data[:-1])[1:-1]

        print raw_data

        dynamicData = struct.pack(fmt2,
            raw_data[0],
            raw_data[1],
            raw_data[2],
            raw_data[3],
            raw_data[4],
            raw_data[5],
            raw_data[6],
            raw_data[7],
            raw_data[8],
            raw_data[9],
            raw_data[10],
            raw_data[11],
            raw_data[12],
            raw_data[13],
            raw_data[14],
            raw_data[15],
            raw_data[16],
            raw_data[17],
            raw_data[18],
            raw_data[19],
            raw_data[20],
            raw_data[21],
            raw_data[22],
            raw_data[23],
            raw_data[24],
            raw_data[25],
            raw_data[26],
            raw_data[27],
            raw_data[28],
            raw_data[29],
            raw_data[30])


        #data_to_send = staticData + dynamicData

        data_to_send = dynamicData

        #print data_to_send
        
        #convert tuple to string and remove the parentheses on the ends
        #data_to_send = str(data_tuple).strip("()")

        # Publish the data to the exchange
        self.channel.basic_publish(exchange=self.logName,
                                   routing_key=self.RoutingKey,
                                   body=data_to_send) #used to be body=data (from Pilot)

        #tony was here
        print("Sending: %r via %r and %r" % (data,self.logName,self.RoutingKey))

        self.connection.close()

    def stop(self):
        """
        Stop the UDP Socket
        """

        # Set the running flag to false, the listener won't actually stop until
        # the next message is received, or a timeout is reached.
        self.keep_running = False
