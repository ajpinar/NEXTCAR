#from __future__ import print_function
import struct


####
####    THIS IS DESIGNED FOR "Data_Interface_for_Communication_02_02_2018.xlsx"
####

####
####    MUST BE RETROFITTED TO "Data_Interface_for_Communication_06_27_2018.xlsx"
####

MEpad = [ 0 for c in range(19) ]
CEpad = [0, 0.0]
processed = None

#CEdataFormat= '!Hdddiiddddddddddi'
CEdataFormat = '!Hdddiiddddddddddidd'       # If data isn't recognized, change "H" to "i"
MEdataFormat = '!id'
CONCdataFormat = '!idHdddiiidddddddddddd'

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


    if type(body) is bytes and not type(body) is str:
        if len(body) is ( 8 * CEdataFormat.count('d') + 4 * CEdataFormat.count('i') + 2 * CEdataFormat.count('H') ):
            # CE data packet
            # 134 bytes is:
            # 15 doubles (8 bytes)
            # 3 integers (4 bytes)
            # 1 short ( 2 bytes)


            #data = list(struct.unpack(CEdataFormat, body)) #### Updated to work with 06_27_2018
            #data.insert(-10, data.pop())                   ####
            
            data = list(struct.unpack(CEdataFormat, body))  ####    Unpacks with new CEdataFormat
            data.insert(-10,data.pop())                     ####    Removes last piece of data and puts it in front of arrays
            data.insert(-11,data.pop())                     ####    Removes new last piece and puts it in front of previous data
            data.insert(-12,data.pop())                     ####    Removes new last piece and puts it in front of previous data
            
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
                                    data[18],
                                    data[19],
                                    data[20])

            print 'CE data packet.'
            print type(body)
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',str(body)
            print 'New packet:',str(processed)

                
        elif len(body) is ( 8 * MEdataFormat.count('d') + 4 * MEdataFormat.count('i') ):
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
                                    data[18],
                                    data[19],
                                    data[20])

            print 'ME data packet.'
            print type(body)
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',str(body)
            print 'New packet:',str(processed)

            
        else:
            print 'Data packet format unknown.'
            print type(body)
            print 'Packet:',str(body)
            print 'Packet size:',len(body)

    elif type(body) is str:
        
        data = body.split(',')
        
        if not len(body) is 2:              # This needs to be more accurate
            # CE data packet as string

            data.insert(6, data.pop())
            data.insert(6, data.pop())    ####    Updated to work with 06_27_2018
            data.insert(6, data.pop())    ####    Updated to work with 06_27_2018
            pdata = CEpad + data

            for c in range(len(pdata)):
                if c in [0,2,6,7,8]:
                    pdata[c] = int(pdata[c])
                else:
                    pdata[c] = float(pdata[c])

            processed = struct.pack(CONCdataFormat,
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
            #print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',str(body)
            #print 'New packet:',processed.encode('ascii')
            
        elif len(body) is 2:
            # ME data packet as string
            # unknown as of 6/15/18, 11:30AM
            # speed limit and grade, as of 6/15/18, 1PM

            pdata = data + MEpad

            for c in range(len(pdata)):
                if c in [0,2,6,7,8]:
                    pdata[c] = int(pdata[c])
                else:
                    pdata[c] = float(pdata[c])

            processed = struct.pack(CONCdataFormat,
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
            print 'Old packet size:',len(body)
            print 'New packet size:',len(processed)
            print 'Old packet:',str(body)
            print 'New packet:',processed

        else:
            print 'Data packet format unknown.'
            print 'This shouldn''t even be possible.'
            print body
            print len(body),'characters'
    else:
        print 'Data packet format unknown.'
        print 'Packet:',body
        print type(body)
        print len(body)

    if not processed is None:
        return processed



# Test information

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

MEbyte = struct.pack(MEdataFormat,
                     25,
                     2.5)

CEstring = '0,1,1.3,5,13,5,35,35,35,35,35,25,25,25,25,25,13,0,0'        # datum

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

#process(CEstring)


