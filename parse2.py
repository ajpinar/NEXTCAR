import struct

MEpad = [ 0 for c in range(17) ]
CEpad = [0, 0.0]
processed = None

CEdataFormat = '!Hdddiiddddddddddi'
MEdataFormat = '!id'
CONCdataFormat = '!idHdddiiidddddddddd'

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


    if type(body) is bytes:
        if len(body) is 118:
            # CE data packet
            # 120 bytes is:
            # 13 doubles (8 bytes)
            # 4 integers (4 bytes)


            data = list(struct.unpack(CEdataFormat, body))
            data.insert(-10, data.pop())
            data = CEpad + data
            processed = struct.pack(CONCdataFormat,
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
                                    data[18])

            print 'CE data packet.'
            print type(body)
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',body
            print 'New packet:',processed
            
        elif len(body) is 12:
            # ME data packet
            # unknown as of 6/15/18, 11:30AM
            # speed limit and grade, as of 6/15/18, 1PM
            # 12 bytes is
            # 1 integer (4 bytes)
            # 1 double (8 bytes)


            data = list(struct.unpack(MEdataFormat, body))
            data = data + MEpad
            processed = struct.pack(CONCdataFormat,
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
                                    data[18])
            
            print 'ME data packet.'
            print type(body)
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',body
            print 'New packet:',processed
            
        else:
            print 'Data packet format unknown.'
            print type(body)
            print 'Packet:',body,
            print 'Packet size:',len(body)
    elif type(body) is str:
        if len(body) > 10:      # This needs to be more accurate
            # CE data packet as string

            
            data = body.split(',')
            data.insert(-10, data.pop())
            pdata = CEpad + data
            processed = ''
            for string in pdata:
                processed = processed + ',' + str(string)
            processed = processed[1:]

            print 'CE data packet.'
            print type(body)
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',body
            print 'New packet:',processed
            
        elif len(body) is 2:
            # ME data packet as string
            # unknown as of 6/15/18, 11:30AM
            # speed limit and grade, as of 6/15/18, 1PM

            
            data = body.split(',')
            pdata = data + MEpad
            processed = ''
            for string in pdata:
                processed = processed + ',' + str(string)
            processed = processed[1:]

            print 'ME data packet.'
            print type(body)
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',body
            print 'New packet:',processed

        else:
            print 'Data packet format unknown.'
            print body
            print len(body),'characters'
    else:
        print 'Data packet format unknown.'
        print 'Packet:',body
        print type(body)

    if not processed is None:
        return processed



# Test information

datum = '0,0.1,1.5,5,15,5,35,35,35,35,35,25,25,25,25,25,1'

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
                     SIM_INDEX)

MEbyte = struct.pack(MEdataFormat,
                     25,
                     2.5)

CEstring = datum

MEstring = '25,2.5'

NAbyte = struct.pack('!iiii',
                     1,
                     2,
                     3,
                     4)

NAstring = '1,2,3,4'



# Argument is one of the following

# CEbyte    -> a representation of data from CE department
# MEbyte    -> a representation of data from ME department
# CEstring  -> a string representation of CE data, unused
# MEstring  -> a string representation of ME data, unused
# NAbyte    -> a non-applicable assortment of data
# NAstring  -> a non-applicable string assortment of data, unused

process(CEbyte)


