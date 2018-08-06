import threading
import pika
import os
import struct
import socket

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
        self.params = pika.ConnectionParameters(self.serverip,
                                   5672,
                                   '/',
                                   self.credentials)                  # Set Pika parameters
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
        #this extracts the data to a tuple
        data_tuple = struct.unpack("<hddhdddddddddddd", data)
        #convert tuple to string and remove the parentheses on the ends
        data_to_send = str(data_tuple).strip("()")

        # Publish the data to the exchange
        self.channel.basic_publish(exchange=self.logName,
                      routing_key=self.RoutingKey,
                      body=data_to_send) #used to be body=data (from Pilot)

        #tony was here
        #print("Sending: %r via %r and %r" % (data,self.logName,self.RoutingKey))

        self.connection.close()

    def stop(self):
        """
        Stop the UDP Socket
        """

        # Set the running flag to false, the listener won't actually stop until
        # the next message is received, or a timeout is reached.
        self.keep_running = False