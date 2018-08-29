"""

Author: Sam Celani

File:   parse.py

Description:

    This script listens to wireless communications sent from the vehicle to the
    cloud (mobile lab). It then looks up the approximate road grade and speed limit
    from imported files, and sends them back to the vehicle using send.py.
    
    It is part of the ARPA-E Project: NEXTCAR.

NOTE:

    BECAUSE THIS FILE HAS A .pyc COMPANION FILE, ANY FUNCTIONAL CHANGE
    TO THIS FILE WILL REQUIRE THE ERASURE OF THE COMPANION FILE
    
"""

####
####    THIS IS DESIGNED FOR "Data_Interface_for_Communication_06_27_2018.xlsx"
####

###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:
    
    import struct       ##  Used for data unpacking     | 

except Exception as ex:
    print ex
    exit()

###########################################################

#
#   Global Variables
#   

MEpad = [ 0 for c in range(19) ]    ##  Gets appended to an incoming data packet from the Mechanical Department
CEpad = [0, 0.0]                    ##  Gets prepended to an incoming data packet from the Civil Department
processed = None                    ##  Initialized as None, only changes if a recognized packed is recieved

CEdataFormat = '!Hdddiiddddddddddidd'       ##  Supposed format of the Civil data packet, as of 8/12/18
MEdataFormat = '!id'                        ##  Supposed format of the Mechanical data packet, as of 8/12/18
CONCdataFormat = '!idHdddiiidddddddddddd'   ##  Supposed format of the concatenated data packet, derived from CE and ME data formats

###########################################################

#
#   FUNCTION DEFINITION 1
#       Checks to see if the data is of a known format,
#       processes it, and returns it
#

def process(body):
    # check size to decipher between CE or ME data
    # check type of data (string, bytes-like object, struct)
    # parse and shift data over, repack
    # fill in missing pieces
    # return

    global MEpad
    global CEpad
    global processed

    global CEdataFormat
    global MEdataFormat
    global CONCdataFormat


    if type(body) is bytes and not type(body) is str:       ##  Strings are also of type 'bytes', but we don't want strings
        if len(body) is ( 8 * CEdataFormat.count('d') + 4 * CEdataFormat.count('i') + 2 * CEdataFormat.count('H') ):        ##  Determine if the length matches the Civil data format
            # CE data packet
            # 134 bytes is:
            # 15 doubles (8 bytes)
            # 3 integers (4 bytes)
            # 1 short ( 2 bytes)
            
            data = list(struct.unpack(CEdataFormat, body))  ##  Unpacks with CEdataFormat
            data.insert(-10,data.pop())                     ##  Removes last piece of data and puts it in front of arrays
            data.insert(-11,data.pop())                     ##  Removes new last piece and puts it in front of previous data
            data.insert(-12,data.pop())                     ##  Removes new last piece and puts it in front of previous data

            ##  This is done to move random numbers after the arrays, for the ease of processing the data in Simulink

            
            data = CEpad + data                             ##  Concatenates data packet with padding
            processed = struct.pack(CONCdataFormat,         ##  Converts the concatenated data list into bytes
                                    data[0],
                                    data[1],
                                    data[2],
                                    data[3],
                                    data[4],
                                    data[5],
                                    data[6],
                                    data[7],
                                    data[8],
                                    data[9],
                                    data[10],
                                    data[11],
                                    data[12],
                                    data[13],
                                    data[14],
                                    data[15],
                                    data[16],
                                    data[17],
                                    data[18],
                                    data[19],
                                    data[20])

            print 'CE data packet.'
            print type(body)
            print 'Old packet size: ' + str(len(body))
            print 'New packet size: ' + str(len(processed))
            print 'Old packet: ' + str(body)
            print 'New packet: ' + str(processed)

                
        elif len(body) is ( 8 * MEdataFormat.count('d') + 4 * MEdataFormat.count('i') ):        ##  Determine if the length matches the Mechanical data format
            # ME data packet
            # speed limit and grade, as of 6/15/18, 1PM
            # 12 bytes is
            # 1 integer (4 bytes)
            # 1 double (8 bytes)


            data = list(struct.unpack(MEdataFormat, body))      ##  Unpacks with MEdataFormat
            
            data = data + MEpad                                 ##  Concatenates data packet with padding
            processed = struct.pack(CONCdataFormat,             ##  Converts the concatenated data list into bytes
                                    data[0],
                                    data[1],
                                    data[2],
                                    data[3],
                                    data[4],
                                    data[5],
                                    data[6],
                                    data[7],
                                    data[8],
                                    data[9],
                                    data[10],
                                    data[11],
                                    data[12],
                                    data[13],
                                    data[14],
                                    data[15],
                                    data[16],
                                    data[17],
                                    data[18],
                                    data[19],
                                    data[20])

            print 'ME data packet.'
            print type(body)
            print 'Old packet size: ' + str(len(body))
            print 'New packet size: ' + str(len(processed))
            print 'Old packet: ' + str(body)
            print 'New packet: ' + str(processed)

            
        else:       ##  This happens if the message matches neither data packet
            print 'Data packet format unknown.'
            print type(body)
            print 'Packet: ' + str(body)
            print 'Packet size: ' + str(len(body))

    elif type(body) is str:     ##  This will happen if the message is a string
        
        data = body.split(',')      ##  Splits data into a list around each comma, which is used as a delimiter in the packet
        
        if not len(body) is 2:              ##  This needs to be more accurate
            # CE data packet as string

            data.insert(6, data.pop())      ##  Reorders data to work with Simulink
            data.insert(6, data.pop())      ##  Reorders data to work with Simulink
            data.insert(6, data.pop())      ##  Reorders data to work with Simulink
            pdata = CEpad + data            ##  Concatenate data packet with padding

            for c in range(len(pdata)):                 ##  These values are a list of strings
                if c in [0,2,6,7,8]:                    ##  Values in these positions need to be integers
                    pdata[c] = int(pdata[c])            ##  Converts to integers
                else:                                   ##  Otherwise, they need to be floats
                    pdata[c] = float(pdata[c])          ##  Convert to floats

            processed = struct.pack(CONCdataFormat,     ##  Converts the concatenated data list into bytes
                        pdata[0],
                        pdata[1],
                        pdata[2],
                        pdata[3],
                        pdata[4],
                        pdata[5],
                        pdata[6],
                        pdata[7],
                        pdata[8],
                        pdata[9],
                        pdata[10],
                        pdata[11],
                        pdata[12],
                        pdata[13],
                        pdata[14],
                        pdata[15],
                        pdata[16],
                        pdata[17],
                        pdata[18],
                        pdata[19],
                        pdata[20])

            print 'CE data packet.'
            print type(body)
            print 'New packet size: ' + str(len(processed))
            print 'Old packet: ' + str(body)
            
        elif len(body) is 2:                    ##  This is the ME data packet
            # ME data packet as string
            # unknown as of 6/15/18, 11:30AM
            # speed limit and grade, as of 6/15/18, 1PM

            pdata = data + MEpad            ##  Concatenate data packet with padding

            for c in range(len(pdata)):                 ##  These values are a list of strings
                if c in [0,2,6,7,8]:                    ##  Values in these positions need to be integers
                    pdata[c] = int(pdata[c])            ##  Converts to integers
                else:                                   ##  Otherwise, they need to be floats
                    pdata[c] = float(pdata[c])          ##  Convert to floats

            processed = struct.pack(CONCdataFormat,     ##  Converts the concatenated data list into bytes
                        pdata[0],
                        pdata[1],
                        pdata[2],
                        pdata[3],
                        pdata[4],
                        pdata[5],
                        pdata[6],
                        pdata[7],
                        pdata[8],
                        pdata[9],
                        pdata[10],
                        pdata[11],
                        pdata[12],
                        pdata[13],
                        pdata[14],
                        pdata[15],
                        pdata[16],
                        pdata[17],
                        pdata[18],
                        pdata[19],
                        pdata[20])

            print 'ME data packet.'
            print type(body)
            print 'Old packet size: ' + str(len(body))
            print 'New packet size: ' + str(len(processed))
            print 'Old packet: ' + str(body)
            print 'New packet: ' + str(processed)

        else:       ##  This literally shouldn't be possible, idk why I added this, -Sam
            print 'Data packet format unknown.'
            print 'This shouldn''t even be possible.'
            print body
            print str(len(body)) + 'characters'
    else:           ##  This happens if the data packet is neither a string nor a byte stream
        print 'Data packet format unknown.'
        print 'Packet:',body
        print type(body)
        print len(body)

    ##  The processed variable is only changed if a data format is known
    if not processed is None:       ##  If processed isn't still None, i.e. the data format is known and processed has a value
        return processed            ##  return it


###########################################################

#
#   TESTING
#

##  Splits a sample test data sample and packs it into bytes as a test packet
datum = '0,0.1,1.5,5,15,5,35,35,35,35,35,25,25,25,25,25,1,0.0,0.0'

sampleData = datum.split(',')

VEHICLE_ID = int(sampleData[0])
SIMULATION_TIME_STEP = float(sampleData[1])
CURRENT_TIME = float(sampleData[2])
PREDICTION_HORIZON = float(sampleData[3])
CLOUD_MESSAGE_ID = int(sampleData[4])
NUM_STEP = int(sampleData[5])
PREDICTED_VEHICLE_UVELOCITY = sampleData[6:11]
PREDICTED_VEHICLE_LVELOCITY = sampleData[11:16]
SIM_INDEX = int(sampleData[16])
DESIRED_ACCEL = float(sampleData[17])
DESIRED_VEL = float(sampleData[18])

##  Byte-based packed to look like the Civil packet
CEbyte = struct.pack(CEdataFormat,
                     VEHICLE_ID,
                     SIMULATION_TIME_STEP,
                     CURRENT_TIME,
                     PREDICTION_HORIZON,
                     CLOUD_MESSAGE_ID,
                     NUM_STEP,
                     float(PREDICTED_VEHICLE_UVELOCITY[0]),
                     float(PREDICTED_VEHICLE_UVELOCITY[1]),
                     float(PREDICTED_VEHICLE_UVELOCITY[2]),
                     float(PREDICTED_VEHICLE_UVELOCITY[3]),
                     float(PREDICTED_VEHICLE_UVELOCITY[4]),
                     float(PREDICTED_VEHICLE_LVELOCITY[0]),
                     float(PREDICTED_VEHICLE_LVELOCITY[1]),
                     float(PREDICTED_VEHICLE_LVELOCITY[2]),
                     float(PREDICTED_VEHICLE_LVELOCITY[3]),
                     float(PREDICTED_VEHICLE_LVELOCITY[4]),
                     SIM_INDEX,
                     DESIRED_ACCEL,
                     DESIRED_VEL)

##  Byte-based packed to look like the Mechanical packet
MEbyte = struct.pack(MEdataFormat,
                     25,
                     2.5)

##  String-based packed to look like the Civil packet
CEstring = '0,1,1.3,5,13,5,35,35,35,35,35,25,25,25,25,25,13,0,0.0'        # datum

##  String-based packed to look like the Mechanical packet
MEstring = '25,2.5'

##  Byte-based packed to look like a packet that doesn't work
NAbyte = struct.pack('!iiii',
                     1,
                     2,
                     3,
                     4)

##  String-based packed to look like a packet that doesn't work
NAstring = '1,2,3,4'



# Argument is one of the following

"""

CEbyte    -> a representation of data from CE department
MEbyte    -> a representation of data from ME department
CEstring  -> a string representation of CE data, unused
MEstring  -> a string representation of ME data, unused
NAbyte    -> a non-applicable assortment of data
NAstring  -> a non-applicable string assortment of data, unused

"""

#process(CEstring)


