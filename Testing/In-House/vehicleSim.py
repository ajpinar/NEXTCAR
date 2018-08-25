import pika
import sys
import time
import configInit
import numpy as np

default = 10
freq = None


SERVERIP = '141.219.181.216'    ##  Kuilin's server ip
SERVERIP = '141.219.205.25'     ##  Sam's server IP
SERVERIP = '166.152.103.250'    ##  Mobile lab
CREDENTIALS = pika.PlainCredentials('aps-lab', 'aps-lab')       ##  username/password, must be setup on server
LOGNAME = 'cacc_test_exchange'  ##  Exchange name
ROUTING_KEY = 'cloud_cacc'      ##  Routing key


messPart1 = '0.0, 0, 172058.3, 0.0, 0.0, 0.0, 0.0, False, 0.0, 0.0, '
lat = 47.169696
messPart2 = ', -88.5077225, 336.3, False, 1.1764709999999998, -4.5, 336.96000000000004, 0.0, -15.5, 0.0, 0.0, 10.584623497338553, 19.31522194'

index = [ 2*np.pi*c/100 for c in range(100) ]

if len(sys.argv) is 1:
    freq = default
    print('To implement your own desired frequency, try "python [FILENAME].py [FREQ]"')
    print('Proceeding with default frequency: %d' % default)
else:
    freq = int(sys.argv[1])
    print('Proceeding with input frequency: %d' % freq )


period = 1/freq


try:
    # kuilin, beta, sam, mobile_lab, tony_url
    datum = configInit.init('tony_url')
    SERVERIP = datum[0]
    if len(datum) is 3:
        ROUTING_KEY = datum[1]
        LOGNAME = datum[2]
        PARAMS = pika.URLParameters(SERVERIP)
        print( SERVERIP, LOGNAME, ROUTING_KEY ,sep='\n',end='\n\n')
    elif len(datum) is 4:
        credA = datum[1][0]
        credB = datum[1][1]
        if not datum[1][0] is None:
            CREDENTIALS = pika.PlainCredentials(credA,credB)
            PARAMS = pika.ConnectionParameters(SERVERIP,
                                               5672,
                                               '/',
                                               CREDENTIALS)
        else:
            CREDENTIALS = None
            PARAMS = pika.ConnectionParameters(SERVERIP)
        ROUTING_KEY = datum[2]
        LOGNAME = datum[3]

        print( SERVERIP, "("+credA+', '+credB+")", LOGNAME, ROUTING_KEY ,sep='\n',end='\n\n')
    else:
        pass
except:
    PARAMS = pika.ConnectionParameters(SERVERIP,
                                       5672,
                                       '/',
                                       CREDENTIALS)

connection = pika.BlockingConnection(PARAMS)

channel = connection.channel()

channel.exchange_declare(exchange = LOGNAME,
                         exchange_type = 'topic',
                         auto_delete = True)

i = 0
add = 1

s = np.sin(index)

while True:
    if add < 0:
        newLat = -s[i] + lat,0
    else:
        newLat = s[i] + lat,0
    message = messPart1 + str(newLat).split(',')[0][1:] + messPart2


    channel.basic_publish(exchange = LOGNAME,
                          routing_key = ROUTING_KEY,
                          body = message)

    print(' [x] Sent message')
    
    if abs(i) >= len(index) or i is 0:
        add = add * -1
    i = i + add
    time.sleep(period)
