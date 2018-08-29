"""

Author: Sam Celani
        Pilot Systems

File:   RabbitMQ_Rx.py

Description:

    This file consumes data sent wirelessly, and sends
    it over UDP to the MABX.
    
    It is part of the ARPA-E Project: NEXTCAR.

Imported Files:

    parse.py

        Used for padding received data packet.
    
"""


###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:

    import parse        ##  Used for padding the data packet
    import pika         ##  Used for data communications
    import socket       ##  Used for UDP communications to the MABX
    import threading    ##  Used for running the consumer in a seperate thread
    
except Exception as ex:
    print ex
    exit()

###########################################################

#
#   CLASS DEFINITION 1
#


class Consumer:

    #######################################################

    #
    #   FUNCTION DEFINITION 1
    #       Initializes variables
    #


    def __init__(self, SERVERIP, CREDENTIALS, IP, PORT, REMOTEIP, LOGNAME, ROUTING_KEY):

        """
        Parmeters:

        SERVERIP                =   (string)                    IP address for ther cloud server
        CREDENTIALS             =   (pika.PlainCredentials)     Credentials to log into cloud server
        IP                      =   (string)                    The IP address for the UDP connection to the MABX (i.e. "127.0.0.1").
        PORT                    =   (int)                       The port for the UDP socket.
        LOGNAME                 =   (string)                    The name of the Rabbit MQ logger exchange.
        UNIQUE_ROUTING_KEY      =   (string)                    The name of the Rabbit MQ routing key.
        """

        ##  Set the Rabbit MQ server IP
        self.serverip = SERVERIP
        
        ##  Set Rabbit MQ credentials
        self.credentials = CREDENTIALS

        ##  Determine if the server uses credentials
        if self.credentials is None:
            ##  Determine if the URL server is being used
            if '@' in self.serverip:
                self.params = pika.URLParameters(self.serverip)
            ##  This is most likely my local server, should never actually be used  -Sam
            else:
                self.params = pika.ConnectionParameters(self.serverip)
                print 'Warning: You are using a server without credentials.'
                print 'This is not recommended.'
        else:
            self.params = pika.ConnectionParameters(self.serverip,
                                                    5672,
                                                    '/',
                                                    self.credentials)

        ##  Log name should match the Publisher's name
        self.logName = LOGNAME

        ##  Set routing keys used to receive info from
        self.routing_key = ROUTING_KEY
        
        self.params.socket_timeout = None       ##  Initialize socket timeout
        self.connection = None                  ##  Initialize Connection object
        self.channel = None                     ##  Initialize Channel object


        ##  Set the UDP parametes
        self.UDP_IP = IP
        self.UDP_PORT = PORT
        self.remoteIP = REMOTEIP
        self.sock = socket.socket(socket.AF_INET,       ##  Internet
                     socket.SOCK_DGRAM)                 ##  UDP

    #######################################################

    #
    #   FUNCTION DEFINITION 2
    #       Starts the consumer on a separate thread
    #

    def start(self):
        """
        Start the consumer in a separate thread.
        Must be stopped by the caller
        """
        self.th = threading.Thread(target=self.receiveLog)
        self.th.daemon = True                                       # Thread will terminate with the main
        self.th.start()
        self.th.join(0)

    #######################################################

    #
    #   FUNCTION DEFINITION 3
    #       Makes connections and consumes
    #

    def receiveLog(self):
        """ Create a logger type of exchange so messages can be sent to multiple receivers. """

        try:
            ##  Bind to the host IP/SOCKET so that the messages don't go out over the default internet connection
            self.sock.bind((self.UDP_IP, self.UDP_PORT))

            ##  Establish the RabbitMQ connection
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()

            ##  Declare exchange
            self.channel.exchange_declare(exchange=self.logName,
                                          exchange_type='topic',
                                          auto_delete = True)

            ##  Set up a random queue for the consumer.
            result = self.channel.queue_declare(exclusive=True)

            ##  Get the random queue name
            queue_name = result.method.queue

            ##  Bind exchange to queue
            self.channel.queue_bind(exchange=self.logName,
                       queue=queue_name,
                       routing_key=self.routing_key)

            ##  Set up the consumer and set the callback function when a message is received
            self.channel.basic_consume(self.callback,
                                       queue=queue_name,
                                       no_ack=True)

            ##  Start the consumer
            print "  Started RabbitMQ Consumer Log:  {}".format(self.logName)
            self.channel.start_consuming()

        finally:
            ##  Gracefully close all connections upon normal or error exit
            if self.connection is not None:
                self.channel.stop_consuming()
                self.connection.close()
                print "  Stopped RabbitMQ Consumer Log:  {}".format(self.logName)

            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print "  UDP {0}::{1} Shutdown".format(self.UDP_IP, self.UDP_PORT)

    #######################################################

    #
    #   FUNCTION DEFINITION 4
    #       Function to be called when data is received
    #

    def callback(self, ch, method, properties, body):
        """Code to perform when a message is received"""
        
        body = parse.process(body)

        # for this routine, the data merely needs to be re-sent on the UDP connection
        # A data validity check may be good to add in the future
        self.sock.sendto(body,(self.remoteIP, self.UDP_PORT))
        print " [x] {}".format(body)
