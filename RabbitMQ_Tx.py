"""

Author: Sam Celani
        Pilot Systems

File:   RabbitMQ_Tx.py

Description:

    This file takes data from the MABX through a socket
    and sends it wirelessly from the car to the cloud, or
    as specified by configInit.py in StartPublisherCont.py.
    
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

    import pika         ##  Used for data communications
    import socket       ##  Used for UDP communications to the MABX
    import struct       ##  Used for data unpacking
    import threading    ##  Used for running the consumer in a seperate thread
    
except Exception as ex:
    print ex
    exit()

###########################################################

#
#   CLASS DEFINITION 1
#


class Publisher:

    #######################################################

    #
    #   FUNCTION DEFINITION 1
    #       Initializes variables
    #


    def __init__(self, SERVERIP, CREDENTIALS, IP, PORT, LOGNAME, ROUTING_KEY):

        """
        Parmeters:

        SERVERIP        =   (string)                    The IP address of the server
        CREDENTIALS     =   (pika.PlainCredentials)     Credentials to log into cloud server
        IP              =   (string)                    The IP address for the UDP connection to the MABX (i.e. "127.0.0.1").
        PORT            =   (int)                       The port for the UDP socket.
        LOGNAME         =   (string)                    The name of the Rabbit MQ logger exchange.
        ROUTING_KEY     =   (string)                    The name of the Rabbit MQ routing key.
        """

        ##  Set the Rabbit MQ server IP
        self.serverip = SERVERIP

        ##  Set Rabbit MQ credentials
        self.credentials = CREDENTIALS

        ##  Determine if the server uses credentials
        if self.credentials is None:
            ##  Determine if the URL server is being used
            if '@' in self.serverip:
                self.params = pika.URLParameters(urlT)
            ##  This is most likely my local server, should never actually be used  -Sam
            else:
                self.params = pika.ConnectionParameters(self.serverip)
                print 'Warning: You are using a server without credentials.'
                print 'This is not recommended.'
        else:
            self.params = pika.ConnectionParameters(self.serverip,
                                                    5672,
                                                    '/',
                                                    self.credentials,
                                                    socket_timeout = None)

        ##  Log name should match the Publisher's name
        self.logName = LOGNAME

        ##  Set routing keys used to receive info from
        self.routing_key = ROUTING_KEY;
        
        self.connection = None              ##  Declare Connection field
        self.channel = None                 ##  Declare Channel field


        # Set the UDP parametes
        self.keep_running = False                                   ##  Flag for the UDP Listening loop
        self.UDP_IP = IP
        self.UDP_PORT = PORT
        self.sock = socket.socket(socket.AF_INET,                   ##  Internet
                     socket.SOCK_DGRAM)                             ##  UDP

    #######################################################

    #
    #   FUNCTION DEFINITION 2
    #       Starts the producer on a separate thread
    #
    
    def start(self):
        """
        Start the UDP listener in a separate thread.
        """

        self.keep_running = True                                    # Set running flag to true
        self.th = threading.Thread(target=self.listenSocket)
        self.th.daemon = True                                       # Thread will terminate with the main
        self.th.start()
        self.th.join(0)

    #######################################################

    #
    #   FUNCTION DEFINITION 3
    #       Pulls data from socket, and tries to send it
    #
    
    def listenSocket(self):
        """
        Start the UDP Socket
        """

        # Bind to the listening socket.AF_INET
        # It may be good to add a timeout routine later
        try:
            self.sock.settimeout(10.0)
            self.sock.bind((self.UDP_IP, self.UDP_PORT))
            print "  UDP %s::%i Socket Bound".format(self.UDP_IP, self.UDP_PORT)
        
            while self.keep_running:
                try:
                    #pass
                    ##  Pulling data from the MABX
                    data, addr = self.sock.recvfrom(1024)           # buffer size is 1024 bytes
                except socket.timeout as e:
                    if self.keep_running:
                        print "  UDP %s::%i Timeout Occurred".format(self.UDP_IP, self.UDP_PORT)
                    else:
                        pass
                else:
                    ##  Call function that sends data
                    self.callback(data)

        finally:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print "  UDP %s::%i Shutdown".format(self.UDP_IP, self.UDP_PORT)

    def callback(self, data):
        """
        Send the data over the Rabbit MQ Connection
        """

        ##  Establish the RabbitMQ connection with input parameters
        self.connection = pika.BlockingConnection(self.params)

        ##  Establish the RabbitMQ channel from connection
        self.channel = self.connection.channel()

        ##  Declare exchange
        self.channel.exchange_declare(exchange=self.logName,
                                      exchange_type='topic',
                                      auto_delete=True)


        ##  I don't know how to make strings in Simulink, so the IP is added here   -Sam
        ip = '141.219.212.72'       ##  THIS IS HARDCODED, BAD, FIX

        ##  From Data_Interface_for_Communications_06/27/2018.xlsx
        fmt = "<HddHHdiddddd?ddddd?dddddddddi"
        
        ##  From Data_Interface_for_Communications_06/27/2018.xlsx
        fmt2 = "<HsddHHcdiddddd?ddddd?dddddddddi"

        raw_data = list(struct.unpack(fmt,data))    ##  Take MABX data and unpack it
        raw_data.insert(1,ip)                       ##  Add the IP
        raw_data.insert(6,'@')                      ##  Add @ as a delimiter

        print raw_data

        ##  Pack new data up and prepare to send
        data_to_send = struct.pack(fmt2,
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

        ##  Publish a message data_to_send over the exhange self.logName with routing key self.routing_key
        self.channel.basic_publish(exchange=self.logName,
                                   routing_key=self.routing_key,
                                   body=data_to_send)

        print ' [x] Sent %r'.format(data_to_send)

        ##  Close connection
        self.connection.close()

    def stop(self):
        """
        Stop the UDP Socket
        """

        # Set the running flag to false, the listener won't actually stop until
        # the next message is received, or a timeout is reached.
        self.keep_running = False
