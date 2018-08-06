import RabbitMQ_Tx
import time
import pika
#data sent by the vehicle once, upon intitialization
if __name__ == "__main__":
    
    SERVERIP = '166.152.103.250'
    SERVERIP = '35.54.5.207'
    SERVERIP = '141.219.181.216' #Kuilin's server ip
    #SERVERIP = '141.219.205.25' # Sam's server IP
    CREDENTIALS = pika.PlainCredentials('aps-lab', 'aps-lab') #username/password, must be setup on server
    IP = '192.168.150.10'#IP of the UDP connection to the uAutoBox (don't change)
    PORT = 5001
    LOGNAME = 'apsdev_xchg' #exchange name
    ROUTING_KEY = 'cloud_cacc_registration'
    
    pub = RabbitMQ_Tx.Publisher(SERVERIP, CREDENTIALS, IP, PORT, LOGNAME, ROUTING_KEY)
    pub.start()

    print('Script ''StartPublisherInit'' Started.  Press ^C or close window to stop...')
    while True:
        time.sleep(1.0)
        #main loop
        pass