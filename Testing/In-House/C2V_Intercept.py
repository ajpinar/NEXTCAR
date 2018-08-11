#################################################
#   Author: Sam Celani                          #
#   Date:   5/18/18                             #
#                                               #
#   File:   C2V_Intercept.py                    #
#                                               #
#   Description:                                #
#                                               #
#   This script will listen to wireless         #
#   communications sent from the 'cloud' to     #
#   the receiving vehicle as part off the       #
#   ARPA-E Project: NEXTCAR. The data will be   #
#   displayed on the console and written to a   #
#   time stamped file.                          #
#                                               #
#################################################


###########################################################

#
#   IMPORTS
#

import datetime     # Used in file naming               | Function::getTheDate
import pika         # Used in data transmission         | Function::init
import sys          # Used for testing                  | Part::TESTING
import configInit   # Used to switch between servers    | Function::init
import scipy.io     # Used to process GPS data          | Part::TESTING
try:
    import parse    # Used to fix data packet           | Part::TESTING
except:
    pass

###########################################################

#
#   FUNCTION DEFINITION 1
#       Initialization function
#       Initializes connection, exchange, queues, and their bindings

def init(SERVERIP, CREDENTIALS, LOGNAME, UNIQUE_ROUTING_KEY, FANOUT_ROUTING_KEY, FLAG):

    if FLAG:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP,
                                                                       port = 5672,
                                                                       virtual_host = '/',
                                                                       credentials = CREDENTIALS))
                                                                    # Assuming the credentials are valid
    else:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP))

    channel = connection.channel()
    """
#   /   Using information from StartConsumer.py \

    channel.exchange_declare(exchange = LOGNAME,
                             exchange_type = 'topic',
                             auto_delete = True)

    q1 = channel.queue_declare(exclusive = True)
    q1_name = q1.method.queue

    channel.queue_bind(exchange = LOGNAME,
                       queue = q1_name,
                       routing_key = UNIQUE_ROUTING_KEY)
    channel.queue_bind(exchange = LOGNAME,                      # The FANOUT_ROUTING_KEY is
                       queue = q1_name,                         # also given in StartConsumer.py.
                       routing_key = FANOUT_ROUTING_KEY)        # Including because it may be useful

#   \   Using information from StartConsumer.py /
    """


#   /   Using information from the email exchange   \

    channel.exchange_declare(exchange = LOGNAME,   # Assuming exchange is
                             exchange_type = 'topic',           # of type 'topic'
                             auto_delete = True)                # Added literally last minute because we got weird errors
    
#    q2 = channel.queue_declare(queue='cloud_cacc',
#                               auto_delete = True)

    q2 = channel.queue_declare(exclusive = True)

    channel.queue_bind(exchange = LOGNAME,                      # Assuming data transfer
                       queue = q2.method.queue,                 # will use UNIQUE_ROUTING_KEY
                       routing_key = UNIQUE_ROUTING_KEY)        # 'vehicle_2'

#   \   Using information from the email exchange   /


    print(' [*] Waiting for packets...')


#   /   What defines the consumption    \

    channel.basic_consume(callback2,                    #### Change callback2 to callback1
                          queue = q2.method.queue,      #### and q2.method.queue to q1_name
                          no_ack = True)                #### to test consumption from cloud
                                                        #### instead of Kuilin's server

#   \   What defines the consumption    /

#   /   Actual Consumption  \

    try:                            # Consumption encapsulated in
        channel.start_consuming()   # try-finally block to ensure
    except KeyboardInterrupt:       # graceful exit
        exit()

#   \   Actual Consumption  /
    
###########################################################

#
#   FUNCTION DEFINITION 2
#       Splits data and pairs it to the appropriate units    
#           Called by the callback functions

def parse(message):

    mes = str(message).split(',')
    strang =  '%s\t\t\t\t[N/A]\n'       % mes[0]
    strang += '%s\t\t\t\t[s]\n'         % mes[1]
    strang += '%s\t\t\t\t[s]\n'         % mes[2]
    strang += '%s\t\t\t\t[subsecond]\n' % mes[3]
    strang += '%s\t\t\t\t[N/A]\n'       % mes[4]
    strang += '%s\t\t\t\t[N/A]\n'       % mes[5]
    strang += '%s\t[m/s]\n'             % mes[6:11]
    strang += '%s\t[m/s]\n'             % mes[11:16]
    strang += '%s\t\t\t\t[N/A]\n'       % mes[16]
    
    return strang
    
###########################################################

#
#   FUNCTION DEFINITION 3
#       Basic Callback function for StartConsumer.py
#           This is what happens when data is received

def callback1(ch, method, properties, body):
    global filename

    print(' [x] %s\n\n' % body)                             # Print to console

    sanitizedBody = parse(body)                             # Sanitizes message, and pairs with units
    print('Clean:\n'+sanitizedBody)                         # Print to console
    with open('log/C2V_LogFiles/' + filename,'w') as file:      # Open file specificed, in folder 'C2V_LogFiles'
        file.write(sanitizedBody)                           # Write data to file

###########################################################

#
#   FUNCTION DEFINITION 4
#       Basic Callback function for email exchange
#           This is what happens when data is received

def callback2(ch, method, properties, body):

    print(' [x] %s\n\n' % body)                             # Print to console

    filename = getTheDate()

    sanitizedBody = parse(body)                             # Sanitizes message, and pairs with units
    print('Clean:\n'+sanitizedBody)                         # Print to console
    with open('log/C2V_LogFiles/' + filename,'w') as file:      # Open file specificed, in folder 'C2V_LogFiles'
        file.write(str(body) + '\n\n')
        file.write(sanitizedBody)                           # Write data to file
        
    print(' [*] Waiting for packets...')

###########################################################

#
#   FUNCTION DEFINITION 4
#       Basic Callback function for email exchange
#           This is what happens when data is received

def getTheDate():

    timestamp = str(datetime.datetime.now())    # Get time, convert to usable string    --> YYYY-Mo-DD HH:Mi:SS.Millisecond
    timestamp = timestamp.split('.')[0]         # Drop milliseconds                     --> YYYY-Mo-DD HH:Mi:SS
    timestamp = timestamp.replace(' ','_')      # Replace space with underscore         --> YYYY-Mo-DD_HH:Mi:SS
    timestamp = timestamp.replace(':','h',1)    # Replace colon with 'h' for hours      --> YYYY-Mo-DD_HHhMi:SS
    timestamp = timestamp.replace(':','m',1)    # Replace colon with 'm' for minutes    --> YYYY-Mo-DD_HHhMimSS
    timestamp = timestamp + 's'                 # Append 's' for seconds                --> YYYY-Mo-DD_HHhMimSSs

    return 'RabbitMq_Rx_' + timestamp + '.txt'  # Create filename

###########################################################

#
#   FUNCTION DEFINITION 5
#       Takes GPS (Lat, Long) and looks up the speed limit
#           at that position

def gpsSLLookUp( lat, long ):
    global gpsSpeedData

    print(gpsSpeedData[( lat, long )])

###########################################################
    
#
#   FUNCTION DEFINITION 6
#       Takes GPS (Lat, Long) and looks up the road grade
#           at that position

def gpsGradeLookUp( lat, long ):
    global gpsGradeData

    print(gpsGradeData[( lat, long )])

###########################################################

#
#   TESTING
#

# Used to validate the behavior of the callback functions
def callbackTest(body):

    filename = getTheDate()
    parseBody = parse(body)
    
    print(' [x] %s' % body,end='\n\nParsed:\n')
    print(parseBody)
    with open('C2V_LogFiles/' + filename,'w') as file:
        file.write(parseBody)

sampleData = '2,0,0,5,217,5,1,1,1,1,1,2,2,2,2,2,0'
"""
gpsSpeedData = dict()
gpsGradeData = dict()

bigData = scipy.io.loadmat('mtudc_speed_limit_grid_mph')
gpsLat = bigData['GPS_Lat']
gpsLong = bigData['GPS_Long']
gpsMPH = bigData['speed_limit_mph']

biggerData = scipy.io.loadmat('grad_grid_MTUDC_050318_CD_minaux_Beta_043')
for b in range(len(biggerData['grade_grid'])):
    for c in range(len(biggerData['grade_grid'][b])):
        if biggerData['grade_grid'][b][c] > 0 or biggerData['grade_grid'][b][c] < 0:
            gpsGradeData.update( { ( biggerData['latitude'][0][b], biggerData['longitude'][0][c] ) : biggerData['grade_grid'][b][c] } )


for i in range(len(gpsLat)):
    gpsSpeedData.update( { ( gpsLat[i][0], gpsLong[i][0] ) : gpsMPH[i][0] } )

#gpsSLLookUp(sumNum1, sumNum2)
#gpsGradeLookUp(sumNum3, sumNum4) """


if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        callbackTest(sampleData)
        exit()
    elif sys.argv[1] == 'local':
        datum = configInit.init(True, False)
        init('localhost', None, datum[3][0], datum[2][0], 'cloud_fanout', False)
    else:
        datum = configInit.init(True, True)
else:
    datum = configInit.init(False, False)

print(datum,'\n')

# Used to see if the script will run without errors
init(datum[0][0],
     pika.PlainCredentials(datum[1][0], datum[1][1]),
     datum[3][0],
     datum[2][0],               # If this doesn't work, try 'vehicle_2' again
     'cloud_fanout',
     True)

###########################################################
