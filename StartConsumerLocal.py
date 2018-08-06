import sys
import time
sys.path.append('C:\Users\Beta One\Documents\MTU Projects\RabbitMQScripts')

import RabbitMQ_Rx

if __name__ == "__main__":
    
    URL = 'amqp://uewiepfr:CkE6UWTnwSbPErjY8sYxwYBKZc62NAr6@wombat.rmq.cloudamqp.com/uewiepfr'
    IP = '127.0.0.1'
    REMOTEIP = '127.0.0.1'
    PORT = 5002
    LOGNAME = 'StationTx'
    
    con = RabbitMQ_Rx.Consumer(URL, IP, PORT, REMOTEIP, LOGNAME)
    con.start()

    print('Script ''StartConsumerLocal'' Started.  Press ^C or close window to stop...')
    while True:
        #main loop
        time.sleep(1.0)
        pass