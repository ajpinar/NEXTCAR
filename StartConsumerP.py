import RabbitMQ_Rx
import time
# for data inbound to vehicle
if __name__ == "__main__":
    
    URL = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
    IP = '192.168.150.10' #IP of the UDP connection to the uAutoBox (don't change)
    REMOTEIP = '192.168.150.1' #IP of the uAutoBox (don't change)
    PORT = 5002 #UDP port for the uAutoBox (don't change)
    LOGNAME = 'StationTx' #Pilot calls this the logger name, in RabbitMQ speak it is the exchange
    
    con = RabbitMQ_Rx.Consumer(URL, IP, PORT, REMOTEIP, LOGNAME)
    con.start()

    print('Script ''StartConsumer'' Started.  Press ^C or close window to stop...')
    while True:
        time.sleep(1.0)
        #main loop
        pass