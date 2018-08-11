try:
    from __future__ import print_function
except:
    pass

import RabbitMQ_Rx_S
import time
import pika

try:
    import configInit
except:
    print('Using default ')
# for data inbound to vehicle
if __name__ == "__main__":
    
    SERVERIP = '166.152.103.250'    # Mobile Lab?
    #SERVERIP = '35.54.5.207'
    #SERVERIP = '141.219.181.216' # Kuilin's server ip
    #SERVERIP = '141.219.205.25' # Sam's server IP
    CREDENTIALS = pika.PlainCredentials('aps-lab', 'aps-lab') #username/password, must be setup on server
    IP = '192.168.150.10' #IP of the UDP connection to the uAutoBox (don't change)
    REMOTEIP = '192.168.150.1' #IP of the uAutoBox (DON'T CHANGE)
    PORT = 5002 #UDP port for the uAutoBox (don't change)
    LOGNAME = 'cacc_test_exchange' #Pilot calls this the logger name, in RabbitMQ speak it is the exchange

    UNIQUE_ROUTING_KEY = 'controller_1'
    FANOUT_ROUTING_KEY = 'cloud_fanout'
    
    con = RabbitMQ_Rx_S.Consumer(SERVERIP, CREDENTIALS, IP, PORT, REMOTEIP, LOGNAME, UNIQUE_ROUTING_KEY, FANOUT_ROUTING_KEY)
    con.start()

    print('Script ''StartConsumer'' Started.  Press ^C or close window to stop...')
    while True:
        time.sleep(1.0)
        #main loop
        pass
