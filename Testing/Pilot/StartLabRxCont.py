import LabStationRx
import time

if __name__ == "__main__":
    
    URL = 'amqp://uewiepfr:CkE6UWTnwSbPErjY8sYxwYBKZc62NAr6@wombat.rmq.cloudamqp.com/uewiepfr'
    LOGNAME = 'Alpha1Cont'
    # Although the dSpace UDP Packing block is set to big endian, it seems to be encoding little endian??
    # Thus data format for unpacking is little endian.
    dataFORMAT = '<HddHdddddddddddd'

    con = LabStationRx.Consumer(URL, LOGNAME, dataFORMAT)
    con.start()

    print('Script ''StartLabRxCont'' Started.  Press ^C or close window to stop...')
    while True:
        #main loop
        time.sleep(1.0)
        pass