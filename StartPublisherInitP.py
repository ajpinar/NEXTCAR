import RabbitMQ_TxP
import time
#data sent by the vehicle once, upon intitialization
if __name__ == "__main__":
    
    URL = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
    IP = '192.168.150.10'#IP of the UDP connection to the uAutoBox (don't change)
    PORT = 5001
    LOGNAME = 'Alpha1Init'
    
    pub = RabbitMQ_TxP.Publisher(URL, IP, PORT, LOGNAME)
    pub.start()

    print('Script ''StartPublisherInit'' Started.  Press ^C or close window to stop...')
    while True:
        time.sleep(1.0)
        #main loop
        pass