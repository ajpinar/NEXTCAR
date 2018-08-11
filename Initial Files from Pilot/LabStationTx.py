import threading
import pika
import os
import struct
import socket
import time

"""
This class is used to simulate the data transmitted by the lab to the vehicle fleet.
"""

class SendRabbitData:

    def __init__(self, URL, LOGNAME):

        """
        Parmeters:

        URL     =   (string)    The URL of the Rabbit MQ server.
        LOGNAME =   (string)    The name of the Rabbit MQ logger exchange.
        """

        # Set the Rabbit MQ parameters
        self.url = os.environ.get('CLOUDAMQP_URL', URL)             # Parse CLODUAMQP_URL
        self.params = pika.URLParameters(self.url)                  # Set Pika parameters
        self.params.socket_timeout = 5
        self.connection = None                                      # Initialize Connection object
        self.channel = None                                         # Initialize Channel object
        self.logName = LOGNAME                                      # Log name should match the Publisher's name
        self.loopTime = 1.0                                         # Delta time in seconds to send the data
        self.keep_running = False
        
        # Set the data, big endian format
        self.dataFormat = '>Hddidddddddddddd'
        self.VEHICLE_ID = 12345
        self.SIMULATION_TIME_STEP = 0.1
        self.CURRENT_TIME = 234.567
        self.PREDICTION_HORIZON = 6
        self.PREDICTED_VEHICLE_VELOCITY = [34.5,35.1,36.2,38.5]
        self.PREDICTED_VEHICLE_X = [-1234.5432,-1234.5897,-1234.6666,-1234.7632]
        self.PREDICTED_VEHICLE_Y = [-1234.5432,-1234.5897,-1234.6666,-1234.7632]

        # LOWER PORTION SCALARS
        # UPPER PORTION ARRAYS
        self.message = struct.pack(self.dataFormat,
                                   self.VEHICLE_ID,
                                   self.SIMULATION_TIME_STEP,
                                   self.CURRENT_TIME,
                                   self.PREDICTION_HORIZON,
                                   self.PREDICTED_VEHICLE_VELOCITY[0],
                                   self.PREDICTED_VEHICLE_VELOCITY[1],
                                   self.PREDICTED_VEHICLE_VELOCITY[2],
                                   self.PREDICTED_VEHICLE_VELOCITY[3],
                                   self.PREDICTED_VEHICLE_X[0],
                                   self.PREDICTED_VEHICLE_X[1],
                                   self.PREDICTED_VEHICLE_X[2],
                                   self.PREDICTED_VEHICLE_X[3],
                                   self.PREDICTED_VEHICLE_Y[0],
                                   self.PREDICTED_VEHICLE_Y[1],
                                   self.PREDICTED_VEHICLE_Y[2],
                                   self.PREDICTED_VEHICLE_Y[3])

        """
        Data Formatting:
        Char	Byte order		        Size		Alignment
        @	    native			        native		native
        =	    native			        standard	none
        <	    little-endian		    standard	none
        >	    big-endian		        standard	none
        !	    network (= big-endian)	standard	none

        Format	C Type			    Python type		Standard size
        x	    pad byte		    no value
        c       char                string len 1	1
        b	    signed char		    integer			1
        B	    unsigned char		integer			1
        ?	    _Bool			    bool			1
        h	    short			    integer			2
        H	    unsigned short		integer			2
        i	    int			        integer			4
        I	    unsigned int		integer			4
        l	    long			    integer			4
        L	    unsigned long		integer			4
        q	    long long		    integer			8
        Q	    unsigned long long	integer			8
        f	    float			    float			4
        d	    double			    float			8
        s	    char[]			    string
        p	    char[]			    string
        P	    void *			    integer
        """

    def start(self):
        """
        Start the consumer in a separate thread.
        Must be stopped by the caller
        """
        
        self.keep_running = True
        self.th = threading.Thread(target=self.sendData)
        self.th.daemon = True                                       # Thread will terminate with the main
        self.th.start()
        self.th.join(0)

    def sendData(self):
        """
        Send the data over the Rabbit MQ Connection
        """

        while self.keep_running:
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()

            # The fanout exchange broadcasts all the messages it receives to all the queues it knows.
            # That is what we need for our logger.
            self.channel.exchange_declare(exchange=self.logName,
                             exchange_type='fanout')

            # Publish the data to the exchange
            self.channel.basic_publish(exchange=self.logName,
                          routing_key='',
                          body=self.message)

            self.connection.close()

            time.sleep(self.loopTime)

    def stop(self):
        """
        Stop the Transmission of Data
        """

        self.keep_running = False
        