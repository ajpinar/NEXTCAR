import LabStationTx
import time

if __name__ == "__main__":
    
    URL = 'amqp://uewiepfr:CkE6UWTnwSbPErjY8sYxwYBKZc62NAr6@wombat.rmq.cloudamqp.com/uewiepfr'
    LOGNAME = 'StationTx'

    pub = LabStationTx.SendRabbitData(URL, LOGNAME)
    pub.start()

    print('Script ''StartLabTx'' Started.  Press ^C or close window to stop...')
    while True:
        time.sleep(1.0)
        #main loop
        pass