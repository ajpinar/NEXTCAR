import threading
import pika
import os
import struct
import socket

class Publisher:

    def __init__(self, URL, IP, PORT, LOGNAME):

        """
        Parmeters:

        URL     =   (string)    The URL of the Rabbit MQ server.
        IP      =   (string)    The IP address for the UDP connection to the MABX (i.e. "127.0.0.1").
        PORT    =   (int)       The port for the UDP socket.
        LOGNAME =   (string)    The name of the Rabbit MQ logger exchange.
        """

        # Set the Rabbit MQ parameters
        self.url = os.environ.get('CLOUDAMQP_URL', URL)             # Parse CLODUAMQP_URL
        self.params = pika.URLParameters(self.url)                  # Set Pika parameters
        self.connection = None                                      # Declare Connection field
        self.channel = None                                         # Declare Channel object
        self.logName = LOGNAME                                      # Log name should match the Publisher's name

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

    def callback(self, data):
        """
        Send the data over the Rabbit MQ Connection
        """

        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()

        # The fanout exchange broadcasts all the messages it receives to all the queues it knows.
        # That is what we need for our logger.
        self.channel.exchange_declare(exchange=self.logName,
                         exchange_type='fanout')

        # Publish the data to the exchange
        self.channel.basic_publish(exchange=self.logName,
                      routing_key='',
                      body=data)

        self.connection.close()

    def stop(self):
        """
        Stop the UDP Socket
        """

        # Set the running flag to false, the listener won't actually stop until
        # the next message is received, or a timeout is reached.
        self.keep_running = False