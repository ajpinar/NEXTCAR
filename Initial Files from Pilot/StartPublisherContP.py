import RabbitMQ_Tx
import time
#data sent by the vehicle continuously during operation
if __name__ == "__main__":
    
    URL = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
    IP = '192.168.150.10'#IP of the UDP connection to the uAutoBox (don't change)
    PORT = 5000
    LOGNAME = 'Alpha1Cont'
    
    pub = RabbitMQ_Tx.Publisher(URL, IP, PORT, LOGNAME)
    pub.start()

    print('Script ''StartPublisherCont'' Started.  Press ^C or close window to stop...')
    while True:
        time.sleep(1.0)
        #main loop
        pass