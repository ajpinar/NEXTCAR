import threading
import pika
import os
import struct

class Consumer:

    def __init__(self, URL, LOGNAME, dataFORMAT):

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
        self.params.socket_timeout = 5
        self.connection = None                                      # Initialize Connection object
        self.channel = None                                         # Initialize Channel object
        self.logName = LOGNAME                                      # Log name should match the Publisher's name
        self.dataFormat = dataFORMAT


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
            self.channel.stop_consuming()
            self.connection.close()
            print("  Stopped RabbitMQ Consumer Log:  %s" % self.logName)

    def callback(self, ch, method, properties, body):
        """Code to perform when a message is received"""

        print(" UDP Received %s" % str(struct.unpack(self.dataFormat,body)))

