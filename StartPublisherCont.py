"""

Author: Sam Celani
        Pilot Systems

File:   StartPublisher.py

Description:

    This file determines the connection parameters from RabbitMQ_Tx.py.
    This file is essentially obsolete, and could (READ: should) be done
    entirely by configInit.py. In the future, this file might be deleted.
    
    It is part of the ARPA-E Project: NEXTCAR.


Imported Files:

    configInit.py

        Helps to determine where the script should be listening.

    RabbitMQ_Tx.py

        Receives, parses, and ships data to the MABX.
        
"""

###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:

    import configInit       ##  Used to determine connection params
    import pika             ##  Used for wireless communications
    import RabbitMQ_Tx      ##  Actually does the heavy lifting
    import time             ##  Used for sleep function

except Exception as ex:
    print ex
    exit()

###########################################################

    
#data sent by the vehicle continuously during operation
if __name__ == "__main__":

    #######################################################

    #
    #   DEFAULTING VARIABLES
    #
    
    SERVERIP = '166.152.103.250'    ##  Mobile lab
    SERVERIP = '141.219.181.216'    ##  Kuilin's server ip
    SERVERIP = '141.219.205.25'     ##  Sam's server IP
    CREDENTIALS = pika.PlainCredentials('aps-lab', 'aps-lab')       ##  username/password, must be setup on server
    IP = '192.168.150.10'           ##  IP of the UDP connection to the uAutoBox (don't change)
    PORT = 5000                     ##  Not entirely sure what this is, but it seems important
    LOGNAME = 'cacc_test_exchange'  ##  Exchange name
    ROUTING_KEY = 'cloud_cacc'      ##  Routing key

    #######################################################

###########################################################

#
#   USE OF CONFIGINIT
#

try:
    # kuilin, beta, sam, mobile_lab, tony_url
    datum = configInit.init('tony_url')
    SERVERIP = datum[0]
    if len(datum) is 3:
        ROUTING_KEY = datum[1]
        LOGNAME = datum[2]
        
        print SERVERIP
        print LOGNAME
        print ROUTING_KEY
        print '\n'
        
    elif len(datum) is 4:
        credA = datum[1][0]
        credB = datum[1][1]
        if not datum[1][0] is None:
            CREDENTIALS = pika.PlainCredentials(credA,credB)
        else:
            CREDENTIALS = None
        ROUTING_KEY = datum[2]
        LOGNAME = datum[3]
                                           
        print SERVERIP
        print '({0}, {1})'.format(credA, credB)
        print LOGNAME
        print ROUTING_KEY
        print '\n'
        
    else:
        # shouldn't even be possible
        print 'What?'
except:
    print 'Proceeding with default connection information:\n'
    
        print SERVERIP
        print '({0}, {1})'.format(credA, credB)
        print LOGNAME
        print ROUTING_KEY
        print '\n'

###########################################################

pub = RabbitMQ_Tx.Publisher(SERVERIP, CREDENTIALS, IP, PORT, LOGNAME, ROUTING_KEY)
pub.start()

print 'Script ''StartPublisherCont'' Started.  Press ^C or close window to stop...'
while True:
    time.sleep(1.0)
    #main loop
    pass
