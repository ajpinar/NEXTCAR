"""

Author: Sam Celani

File:   C2V_Intercept.py

Description:




Imported Files:

    configInit.py

        Helps to determine where the script should be listening.

    send.py

        One-off script that sends data back upon being called.
    
"""


###########################################################

#
#   IMPORTS
#

try:
    
    import configInit                   ##  Used to decide server       | Function::init
    import matplotlib.pyplot as plt     ##  Used in plotting            | Function::gpsSLLookup
                                        ##                              | Function::gpsRGLookup
                                        ##                              | Function::callback
                                        ##                              | Part::Testing
    
    import numpy as np                  ##  Used in plotting            | Part::Testing
    import pika                         ##  Used in data transmission   | Function::init
    import scipy.io as sp               ##  Used for SL and RG lookup   | Part::body
    import send                         ##  Used to send data           | Function::callback
##    import struct                       ##  Used for data unpacking     | Part::TESTING
    import sys                          ##  Used for testing            | Part::TESTING
    
except Exception as ex:
    print(ex)

###########################################################

#
#   CONFIG
#

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

##  I don't understand this line, but it seems important  -Sam
plt.ion()

print( SERVERIP, "("+credA+', '+credB+")", LOGNAME, ROUTING_KEY ,sep='\n',end='\n\n')

###########################################################

#
#   FUNCTION DEFINITION 1
#       Takes GPS (Lat, Long) and looks up the speed limit
#           at that position

def gpsSLLookUp( lat, long ):
    global gpsSpeedData     ##  Collection of valid Speed Limit coordinates
    global gpsMPH              ##  Valid Speed Limits

##  Finds the difference between all valid points and the live coordinate
    difSL = [(abs(long - gpsSpeedData[0][c]), abs(lat - gpsSpeedData[1][c])) for c in range(len(gpsSpeedData[0]))]
##  Converts difference to distance
    disSL = [ ( ( latDif )**2 + ( longDif )**2 )**0.5 for (latDif, longDif) in difSL ]

##  Finds the minimum of the distances
    m = min(disSL)
##  Finds index of the minimum distance
    i = disSL.index(m)

##  Prints Speed Limit at desired index
    print(gpsMPH[i][0])
##  Prints corresponding Latitude and Longitude of desired speed limit
    print('Lat',gpsSpeedData[0][i],'\nLong',gpsSpeedData[1][i])
    
    return gpsMPH[i][0]     ##  Returns desired speed limit, for use with sending back

###########################################################
    
#
#   FUNCTION DEFINITION 2
#       Takes GPS (Lat, Long) and looks up the road grade
#           at that position

def gpsGradeLookUp( lat, long ):
    global gpsGradeData     ##  Collection of valid Road Grade coordinates
    global rgL              ##  Valid Road Grades

##  Finds the difference between all valid points and the live coordinate
    dif = [(abs(long - gpsGradeData[0][c]), abs(lat - gpsGradeData[1][c])) for c in range(len(gpsGradeData[0]))]
##  Converts difference to distance
    dis = [ ( ( latDif )**2 + ( longDif )**2 )**0.5 for (latDif, longDif) in dif ]

##  Finds the minimum of the distances
    m = min(dis)
##  Finds index of the minimum distance
    i = dis.index(m)

##  Prints Road Grade at desired index
    print(rgL[i])
##  Prints corresponding Latitude and Longitude of desired road grade
    print('Lat',gpsGradeData[0][i],'\nLong',gpsGradeData[1][i])

##  Plots a red X along the drive cycle in the closest point to live GPS coordinates
    plt.scatter(gpsGradeData[1][i],gpsGradeData[0][i],marker = 'x', c = 'red')
##  Shows the plot
    plt.show()

##  I don't understand this line, but it seems important  -Sam
    plt.pause(0.0001)
    
    return rgL[i]       ##  Returns desired road grade, for use with sending back

###########################################################

#
#   FUNCTION DEFINITION 3
#       Callback, this is what happens when data is received
#           

def callback(ch, method, properties, body):
    global logfile      ##  This is the name of the file that the message gets dumped to

    
    if len(sys.argv) is 2 and sys.argv[1].lower == '-v':    ##  V E R B O S E
        print(len(body))                                    ##  Prints how long the message was
        print(type(body))                                   ##  Prints the type of the message
        
    print(' [x] %s\n' % body)               ##  Prints the actual message
    logfile.write(str(data)[1:-1] + '\n')   ##  Writes to logfile

    """
    fmt = "<HsddHHcdiddddd?ddddd?dddddddddH"
    data = struct.unpack(fmt,body)
    """
    
    data = str(body).split(', ')        ##  Splits data into usable chunks
    
    sl = gpsSLLookUp( float(data[13]), float(data[12]) )        ##  Send coordinates to search algorithm
    rg = gpsGradeLookUp( float(data[13]), float(data[12]) )     ##  Send coordinates to search algorithm
    
    plt.scatter(float(data[13]), float(data[12]), c = 'green')  ##  Prints the coordinate 
    plt.show()                                                  ##  Shows the plot

##  I don't understand this line, but it seems important  -Sam
    plt.pause(0.0001)                                           

    send.fullSend(sl, rg)       ##  Send data out


        
    print(' [*] Waiting for packets...')
    
###########################################################

#
#   TESTING
#

##  Initialize road grade data
pltLat = []
pltLong = []
rgL = []

##  Open Speed Limit data
bigData = sp.loadmat('mtudc_speed_limit_grid_mph')

##  Pull data from inside the Speed Limit data set
gpsLat = bigData['GPS_Lat']
gpsLong = bigData['GPS_Long']
gpsMPH = bigData['speed_limit_mph']

##  Open Road Grade data
biggerData = sp.loadmat('grad_grid_MTUDC_050318_CD_minaux_Beta_043')

##  Populate Road Grade data for Lookup and Plotting
for b in range(len(biggerData['grade_grid'])):
    for c in range(len(biggerData['grade_grid'][b])):

##  In the matrix, entries are either nan or a valid value
        
        if biggerData['grade_grid'][b][c] > 0 or biggerData['grade_grid'][b][c] < 0:
        #   Check to see if the value is valid
        
            pltLat.append(biggerData['latitude'][0][b])
            #   Keep track of valid latitudes
            
            pltLong.append(biggerData['longitude'][0][c])
            #   Keep track of valid longitudes
            
            rgL.append(biggerData['grade_grid'][b][c])
            #   Keep track of corresponding road grades


plt.scatter(pltLong, pltLat, marker = '.')      ##  Plot valid lat long pairs
plt.show()                                      ##  Show plot

##  I don't understand this line, but it seems important  -Sam
plt.pause(0.0001)

gpsGradeData = np.array([pltLat, pltLong])      ##  Format Road Grade data for lookup
gpsSpeedData = np.array([gpsLat,gpsLong])       ##  Format Speed Limit data for lookup


###########################################################


# This needs to go
url = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)


##  Define a connection based off of configInit params

##connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP[0],
##                                                               port = 5672,
##                                                               virtual_host = '/',
##                                                               credentials = CREDENTIALS))

##  Make a channel from connection
channel = connection.channel()

##  Declare exchange
channel.exchange_declare(exchange = LOGNAME,                
                         exchange_type = 'topic',    
                         auto_delete = True)      

##  Declare queue
q2 = channel.queue_declare(exclusive = True)

##  Bind queue to exchange
channel.queue_bind(exchange = 'cacc_test_exchange',
                   queue = q2.method.queue,
                   #routing_key = ROUTING_KEY)
                   routing_key = 'cloud_cacc')



##  Create fake logfile for debugging purposes
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


print(' [*] Waiting for packets...')

##  Define consumption
channel.basic_consume(callback,
                      queue = q2.method.queue,
                      no_ack = True)


##  Acutal consumption
    try:
        logfile = open('V2C_logfile.txt','a')       ##  Open the logfile in append mode

                                    ##  Consumption is nested in a try-
        channel.start_consuming()   ##  except block, in the hopes that it
    except KeyboardInterrupt:       ##  handles a KeyboardInterrupt gracefully. 
                                    ##  Spoiler Alert:: It doesn't work very well

        logfile.close()                             ##  Close file before exiting the script
        exit()                                      ##  Exit script
