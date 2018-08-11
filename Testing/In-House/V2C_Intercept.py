import pika
import scipy.io
import sys
import struct
import matplotlib.pyplot as plt
import numpy as np

try:
    import send
except:
    print('Cannot send.')

try:
    import configInit
except:
    print('Unable to import configInit.py.')


## Keeping this for defaulting, in case configInit fails
    
SERVERIP =      ['166.152.103.250', 'Mobile Lab']   # Mobile Lab IP
SERVERIP =      ['141.219.181.216', 'Kuilin']       # Kuilin's IP
credA =         'aps-lab'
credB =         'aps-lab'
CREDENTIALS =   pika.PlainCredentials(credA, credB)
LOGNAME =       'cacc_test_exchangeA'               # I'm convinced this is going to be a major issue
ROUTING_KEY =   'cloud_cacc'                        # Same

try:
    # kuilin, beta, sam, mobile_lab, tony_url
    datum = configInit.init('tony_url')
    SERVERIP = datum[0]
    if len(datum) is 3:
        ROUTING_KEY = datum[1]
        LOGNAME = datum[2]
    elif len(datum) is 4:
        credA = datum[1][0]
        credB = datum[1][1]
        if not datum[1][0] is None:
            CREDENTIALS = pika.PlainCredentials(credA,credB)
        else:
            CREDENTIALS = None
        ROUTING_KEY = datum[2]
        LOGNAME = datum[3]
    else:
        # shouldn't even be possible
        print('What?')
except:
    print('Proceeding with default connection information:\n')


plt.ion()
#fig=plt.figure()

#plt.axis([0,1000,0,1])

print( SERVERIP, "("+credA+', '+credB+")", LOGNAME, ROUTING_KEY ,sep='\n',end='\n\n')

###########################################################

#
#   FUNCTION DEFINITION 1
#       Takes GPS (Lat, Long) and looks up the speed limit
#           at that position

def gpsSLLookUp( lat, long ):
    global gpsSpeedData
    global gpsMPH

    difSL = [(abs(long - gpsSpeedData[0][c]), abs(lat - gpsSpeedData[1][c])) for c in range(len(gpsSpeedData[0]))]
    disSL = [ ( ( latDif )**2 + ( longDif )**2 )**0.5 for (latDif, longDif) in difSL ]

    m = min(disSL)
    i = disSL.index(m)
    
    print(gpsMPH[i][0])
    print('Lat',gpsSpeedData[0][i],'\nLong',gpsSpeedData[1][i])
    #plt.scatter(gpsSpeedData[1][i],gpsSpeedData[0][i],marker = 'x', c = 'yellow')
    plt.show()
    plt.pause(0.0001)
    
    return gpsMPH[i][0]

###########################################################
    
#
#   FUNCTION DEFINITION 2
#       Takes GPS (Lat, Long) and looks up the road grade
#           at that position

def gpsGradeLookUp( lat, long ):
    global gpsGradeData
    global rgL

    dif = [(abs(long - gpsGradeData[0][c]), abs(lat - gpsGradeData[1][c])) for c in range(len(gpsGradeData[0]))]
    dis = [ ( ( latDif )**2 + ( longDif )**2 )**0.5 for (latDif, longDif) in dif ]
    m = min(dis)
    i = dis.index(m)
    
    print(rgL[i])
    print('Lat',gpsGradeData[0][i],'\nLong',gpsGradeData[1][i])
    #plt.scatter(47.1,-88.6,marker = 'x', c = 'red')
    plt.scatter(gpsGradeData[1][i],gpsGradeData[0][i],marker = 'x', c = 'red')
    plt.show()
    plt.pause(0.0001)
    
    return rgL[i]

###########################################################

#
#   FUNCTION DEFINITION 3
#       Basic Callback function for email exchange
#           This is what happens when data is received

def callback(ch, method, properties, body):
    global logfile

    print(len(body))
    print(type(body))
    print(' [x] %s\n' % body)
    
    if len(sys.argv) is 2 and not sys.argv[1].lower == 'test':
        print(' [x] %s\n' % body)
    fmt = "<HsddHHcdiddddd?ddddd?dddddddddH"
    #data = struct.unpack(fmt,body)
    data = str(body).split(', ')
    logfile.write(str(data)[1:-1] + '\n')
    sl = gpsSLLookUp( float(data[13]), float(data[12]) )
    rg = gpsGradeLookUp( float(data[13]), float(data[12]) )
    plt.scatter(float(data[13]), float(data[12]), c = 'green')
    plt.show()
    plt.pause(0.0001)

    send.fullSend(sl, rg)


        
    print(' [*] Waiting for packets...')
    
###########################################################

#
#   TESTING
#

pltLat = []
pltLong = []
rgL = []

bigData = scipy.io.loadmat('mtudc_speed_limit_grid_mph')
gpsLat = bigData['GPS_Lat']
gpsLong = bigData['GPS_Long']
gpsMPH = bigData['speed_limit_mph']


biggerData = scipy.io.loadmat('grad_grid_MTUDC_050318_CD_minaux_Beta_043')

for b in range(len(biggerData['grade_grid'])):
    for c in range(len(biggerData['grade_grid'][b])):
        if biggerData['grade_grid'][b][c] > 0 or biggerData['grade_grid'][b][c] < 0:
            pltLat.append(biggerData['latitude'][0][b])
            pltLong.append(biggerData['longitude'][0][c])
            rgL.append(biggerData['grade_grid'][b][c])


plt.scatter(pltLong, pltLat, marker = '.')
plt.show()
plt.pause(0.0001)
gpsGradeData = np.array([pltLat, pltLong])
gpsSpeedData = np.array([gpsLat,gpsLong])





###########################################################

#   /   Define connection to Tony's Cloud Server    \

url = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)

##connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP[0],
##                                                               port = 5672,
##                                                               virtual_host = '/',
##                                                               credentials = CREDENTIALS))

channel = connection.channel()

#   \   Define connection to Tony's Cloud Server    /                                          

#   /   Using information StartPublisherCont.py \

channel.exchange_declare(exchange = LOGNAME,                
                         exchange_type = 'topic',    
                         auto_delete = True)      
    
#q2 = channel.queue_declare(queue='cloud_cacc',
#                           auto_delete = True)

q2 = channel.queue_declare(exclusive = True)

channel.queue_bind(exchange = 'cacc_test_exchange',                      # Assuming data transfer
                   queue = q2.method.queue,                 # will use ROUTING_KEY
                   #routing_key = ROUTING_KEY)               # 'cloud_cacc_A'
                   routing_key = 'cloud_cacc')

#   \   Using information StartPublisherCont.py /

#   /   Create a fake logfile for debugging purposes    \

if len(sys.argv) is 2 and sys.argv[1].lower() == 'test':
    simStepIndex = 0
    currentTime = 172530.5
    fakePacket1 = "b'1,141.219.181.216,2.5,1.0,1,5,0.1,"
    fakePacket2 = ",10.0,1.5,87,47,True,10.1,1.51,87,47,250,True,10,2560,8,10000,11.0,1.0,0.5,7.7,80'\n"

    with open('V2C_logfileTEST.txt','w') as file:
        for i in range(10):
            simStepIndex += 0.1
            currentTime += 0.1
            file.write(fakePacket1+str(simStepIndex)+','+str(currentTime)+fakePacket2)
    exit()
elif len(sys.argv) is 2 and sys.argv[1].lower() == 'usage':
    print('python',sys.argv[0],'test\t\t\t-> Prints sample logfile with fake data and quits.')
    print('python',sys.argv[0],'[ANYTHING BUT TEST]\t-> Appends data to file only.')
    print('python',sys.argv[0],'\t\t\t-> Appends data to file and prints data to console.')
    exit()

#   \   Create a fake logfile for debugging purposes    /


print(' [*] Waiting for packets...')


#   /   What defines the consumption    \

channel.basic_consume(callback,
                      queue = q2.method.queue,
                      no_ack = True)


#   \   What defines the consumption    /

#   /   Actual Consumption  \

try:
    logfile = open('V2C_logfile.txt','a')   # Consumption encapsulated in
    channel.start_consuming()               # try-finally block to ensure
except KeyboardInterrupt:                   # graceful exit
    logfile.close()
    exit()

#   \   Actual Consumption  /
