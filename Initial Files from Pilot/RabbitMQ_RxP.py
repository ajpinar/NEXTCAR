import threading
import pika
import os
import struct
import socket

class Consumer:

    def __init__(self, URL, IP, PORT, REMOTEIP, LOGNAME):

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
        self.params.socket_timeout = 10
        self.connection = None                                      # Initialize Connection object
        self.channel = None                                         # Initialize Channel object
        self.logName = LOGNAME                                      # Log name should match the Publisher's name

        # Set the UDP parametes
        self.UDP_IP = IP
        self.UDP_PORT = PORT
        self.remoteIP = REMOTEIP
        self.sock = socket.socket(socket.AF_INET,                   # Internet
                     socket.SOCK_DGRAM)                             # UDP

    def start(self):
        """
        Start the consumer in a separate thread.
        Must be stopped by the caller
        """
        self.th = threading.Thread(target=self.receiveLog)
        self.th.daemon = True                                       # Thread will terminate with the main
        self.th.start()
        self.th.join(0)

    def receiveLog(self):
        """ Create a logger type of exchange so messages can be sent to multiple receivers. """

        try:
            # bind to the host IP/SOCKET so that the messages don't go out over the default internet connection
            self.sock.bind((self.UDP_IP, self.UDP_PORT))

            # establish the RabbitMQ connection
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()

            # The fanout exchange broadcasts all the messages it receives to all the queues it knows.
            # That is what we need for our logger.
            self.channel.exchange_declare(exchange=self.logName,
                             exchange_type='fanout')

            # Set up a random queue for the consumer.
            result = self.channel.queue_declare(exclusive=True)

            # Get the random queue name and bind our channel to the queue.
            queue_name = result.method.queue
            self.channel.queue_bind(exchange=self.logName,
                       queue=queue_name)

            # Set up the consumer and set the callback function when a message is received
            self.channel.basic_consume(self.callback,
                          queue=queue_name,
                          no_ack=True)

            # Start the consumer
            print("  Started RabbitMQ Consumer Log:  %s" % self.logName)
            self.channel.start_consuming()

        finally:
            # Gracefully close all connections upon normal or error exit
            if self.connection is not None:
                self.channel.stop_consuming()
                self.connection.close()
                print("  Stopped RabbitMQ Consumer Log:  %s" % self.logName)

            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print("  UDP %s::%i Shutdown" % (self.UDP_IP, self.UDP_PORT))

    def callback(self, ch, method, properties, body):
        """Code to perform when a message is received"""

        # for this routine, the data merely needs to be re-sent on the UDP connection
        # A data validity check may be good to add in the future
        self.sock.sendto(body,(self.remoteIP, self.UDP_PORT))

