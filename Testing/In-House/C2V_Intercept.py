"""

Author: Sam Celani

File:   C2V_Intercept.py

Description:

    This script listens to wireless communications sent from the cloud (mobile lab)
    to the vehicle. It is part of the ARPA-E Project: NEXTCAR.


Imported Files:

    configInit.py

        Helps to determine where the script should be listening.
    
"""


###########################################################

#
#   IMPORTS
#

try:
    
    import configInit   ##  Used to decide server       | Function::init
    import datetime     ##  Used in file naming         | Function::getTheDate
    import pika         ##  Used in data transmission   | Function::init
    import sys          ##  Used for testing            | Part::TESTING

except Exception as ex:
    print(ex)

###########################################################

#
#   FUNCTION DEFINITION 1
#       Initialization function
#           Initializes connection, exchange, queues, and their bindings

def init(SERVERIP, CREDENTIALS, LOGNAME, UNIQUE_ROUTING_KEY, FANOUT_ROUTING_KEY, FLAG):

##  Define the connection parameters and make a connection
    if FLAG:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP,
                                                                       port = 5672,
                                                                       virtual_host = '/',
                                                                       credentials = CREDENTIALS))
    else:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP))

##  Create a channel
    channel = connection.channel()

##  Declare exhange
    channel.exchange_declare(exchange = LOGNAME,
                             exchange_type = 'topic',
                             auto_delete = True)
##  Declare queue
    q2 = channel.queue_declare(exclusive = True)

##  Bind queue to exchange
    channel.queue_bind(exchange = LOGNAME,
                       queue = q2.method.queue,
                       routing_key = UNIQUE_ROUTING_KEY)


    print(' [*] Waiting for packets...')

##  Define a consumption
    channel.basic_consume(callback,
                          queue = q2.method.queue,
                          no_ack = True)

##  Acutal consumption
    try:                            ##  Consumption is nested in a try-
        channel.start_consuming()   ##  xcept block, in the hopes that it
    except KeyboardInterrupt:       ##  handles a KeyboardInterrupt gracefully. 
        exit()                      ##  Spoiler Alert:: It doesn't work very well
    
###########################################################

#
#   FUNCTION DEFINITION 2
#       Basic Callback function for StartConsumer.py
#           This is what happens when data is received

def callback(ch, method, properties, body):

    filename = getTheDate()             ##  Create file to dump data

    print(' [x] %s\n\n' % body)         ##  Print to console

    with open(filename,'w') as file:    ##  Open file specificed
        file.write(sanitizedBody)       ##  Write data to file

###########################################################

#
#   FUNCTION DEFINITION 3
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

"""

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

"""

###########################################################

